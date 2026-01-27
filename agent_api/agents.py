# =====================================================
# IMPORTS (MATCHING YOUR ENVIRONMENT)
# =====================================================

from dotenv import load_dotenv
from agents import Agent, function_tool
from typing import List, Dict
import pandas as pd

# =====================================================
# LOAD ENV
# =====================================================

load_dotenv()

# =====================================================
# GLOBAL DATA
# =====================================================

inventory_df = None


def load_data_new():
    global inventory_df
    if inventory_df is not None:
        return True

    try:
        inventory_df = pd.read_json(
            "../Api/data/CAR_UNIQUE_DATA.json"
        )
        return True
    except Exception as e:
        print("❌ Failed to load vehicle data:", e)
        return False


def ensure_data_loaded():
    if inventory_df is None:
        load_data_new()


# =====================================================
# TOOLS
# =====================================================

@function_tool
def search_vehicles_by_budget(
    max_budget: int,
    min_budget: int = 0,
    limit: int = 10,
    max_per_make: int = 2
) -> List[Dict]:
    ensure_data_loaded()
    global inventory_df

    def get_price(row):
        if isinstance(row.get("msrp"), (int, float)):
            return row["msrp"]
        if isinstance(row.get("price"), (int, float)):
            return row["price"]
        return None

    df = inventory_df.copy()
    df["computed_price"] = df.apply(get_price, axis=1)

    df = df[
        (df["computed_price"].notnull()) &
        (df["computed_price"] >= min_budget) &
        (df["computed_price"] <= max_budget)
    ]

    results = []
    make_count = {}

    for _, row in df.iterrows():
        make = row.get("make")
        if not make:
            continue

        make_count.setdefault(make, 0)
        if make_count[make] < max_per_make:
            results.append(row.drop("computed_price").to_dict())
            make_count[make] += 1

        if len(results) >= limit:
            break

    return results


@function_tool
def search_vehicles_by_type(
    vehicle_type: str,
    limit: int = 20
) -> List[Dict]:
    ensure_data_loaded()
    global inventory_df

    keywords = {
        "suv": ["suv"],
        "crossover": ["crossover"],
        "minivan": ["minivan", "van"],
        "sedan": ["sedan"]
    }

    terms = keywords.get(vehicle_type.lower(), [])
    if not terms:
        return []

    mask = inventory_df["description"].fillna("").str.lower().apply(
        lambda x: any(term in x for term in terms)
    )

    return inventory_df[mask].head(limit).to_dict("records")


@function_tool
def search_eco_vehicles(
    eco_type: str = "any",
    limit: int = 20
) -> List[Dict]:
    ensure_data_loaded()
    global inventory_df

    df = inventory_df.copy()

    submodel = df["submodel"].fillna("").str.lower()
    desc = df["description"].fillna("").str.lower()
    model = df["model"].fillna("")

    electric = (
        submodel.str.contains(r"\belectric\b|\bev\b", regex=True) |
        model.str.contains(r"\bEV\b|Electric", regex=True) |
        desc.str.contains(r"\bfully electric\b|\bev\b|\belectric vehicle\b", regex=True)
    )

    hybrid = (
        desc.str.contains(r"\bhybrid\b|\bplug-in hybrid\b|\bphev\b", regex=True) &
        ~desc.str.contains(r"\bmild hybrid\b", regex=True)
    )

    return df[electric | hybrid].head(limit).to_dict("records")


# =====================================================
# SPECIALIST AGENTS
# =====================================================

budget_recommendation_agent = Agent(
    name="Budget Recommendation Agent",
    instructions="Recommend vehicles strictly based on budget.",
    tools=[search_vehicles_by_budget],
)

family_vehicle_agent = Agent(
    name="Family Vehicle Agent",
    instructions="Recommend SUVs, crossovers, and minivans.",
    tools=[search_vehicles_by_type, search_vehicles_by_budget],
)

eco_vehicle_agent = Agent(
    name="Eco-Friendly Vehicle Agent",
    instructions="Recommend ONLY EVs and full or plug-in hybrids.",
    tools=[search_eco_vehicles, search_vehicles_by_budget],
)


# =====================================================
# ORCHESTRATOR AGENT
# =====================================================

vehicle_recommendation_agent = Agent(
    name="Vehicle Recommendation Orchestrator",
    instructions="""
Interpret user intent and route to correct specialists.
Combine results and return 2–3 best vehicles.
""",
    tools=[
        budget_recommendation_agent.as_tool(
            "budget_specialist",
            "Provides budget-based vehicle recommendations"
        ),
        family_vehicle_agent.as_tool(
            "family_specialist",
            "Provides family-friendly vehicle recommendations"
        ),
        eco_vehicle_agent.as_tool(
            "eco_specialist",
            "Provides eco-friendly EV and hybrid recommendations"
        ),
    ],
)
