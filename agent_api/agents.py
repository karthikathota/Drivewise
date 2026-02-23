# =====================================================
# IMPORTS
# =====================================================

from dotenv import load_dotenv
from agents import Agent, function_tool
from typing import List, Dict
import pandas as pd
import os

# =====================================================
# LOAD ENV
# =====================================================

load_dotenv()

# =====================================================
# GLOBAL DATA
# =====================================================

inventory_df = None


# =====================================================
# DATA LOADER (FIXED ABSOLUTE PATH)
# =====================================================

def load_data_new():
    global inventory_df

    if inventory_df is not None:
        return True

    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))

        data_path = os.path.join(
            base_dir,
            "..",
            "Api",
            "data",
            "CAR_UNIQUE_DATA.json"
        )

        data_path = os.path.abspath(data_path)

        if not os.path.exists(data_path):
            raise FileNotFoundError(f"File not found at {data_path}")

        inventory_df = pd.read_json(data_path)

        print("✅ Vehicle data loaded successfully")
        return True

    except Exception as e:
        print("❌ Failed to load vehicle data:", e)
        return False


def ensure_data_loaded():
    global inventory_df
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

    if inventory_df is None:
        return []

    df = inventory_df.copy()

    def get_price(row):
        if isinstance(row.get("msrp"), (int, float)):
            return row["msrp"]
        if isinstance(row.get("price"), (int, float)):
            return row["price"]
        return None

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

    if inventory_df is None:
        return []

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

    if inventory_df is None:
        return []

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
    instructions="Use ONLY tool output. Summarize make, model, year, price.",
    tools=[search_vehicles_by_budget],
)

family_vehicle_agent = Agent(
    name="Family Vehicle Agent",
    instructions="Use ONLY tool output. Focus SUVs, crossovers, minivans.",
    tools=[search_vehicles_by_type, search_vehicles_by_budget],
)

eco_vehicle_agent = Agent(
    name="Eco-Friendly Vehicle Agent",
    instructions="Use ONLY tool output. Only EV or full/plug-in hybrids.",
    tools=[search_eco_vehicles, search_vehicles_by_budget],
)


# =====================================================
# ORCHESTRATOR AGENT
# =====================================================

vehicle_recommendation_agent = Agent(
    name="Vehicle Recommendation Orchestrator",
    instructions="""
You interpret user intent and call the correct specialist agents.
Recommend exactly 2–3 vehicles.
For each vehicle include:
- Make, model, year
- Price
- Short reason
Never invent data.
Never output raw JSON.
""",
    tools=[
        budget_recommendation_agent.as_tool(
            tool_name="budget_specialist",
            tool_description="Budget vehicle recommendations"
        ),
        family_vehicle_agent.as_tool(
            tool_name="family_specialist",
            tool_description="Family vehicle recommendations"
        ),
        eco_vehicle_agent.as_tool(
            tool_name="eco_specialist",
            tool_description="Eco vehicle recommendations"
        ),
    ],
)


# =====================================================
# UX ENTRY AGENT (NEW)
# =====================================================

vehicle_entry_agent = Agent(
    name="DriveWise UX Agent",
    instructions="""
You are the FINAL presentation layer of DriveWise.

You MUST:
1. Call `core_recommendation_engine`.
2. Take its response and improve readability and engagement.
3. Keep ALL vehicle data exactly as provided.
4. Do NOT invent or modify prices or specs.

FORMAT RULES:
- Add a short friendly intro.
- Present vehicles in clean bullet format.
- Highlight price clearly.
- Add 1-line benefit summary per vehicle.
- Add a confident closing line suggesting next steps.
- Keep response clean and premium.
- Do NOT output JSON.

Tone:
Professional, confident, modern car advisor.
""",
    tools=[
        vehicle_recommendation_agent.as_tool(
            tool_name="core_recommendation_engine",
            tool_description="Main vehicle recommendation engine"
        )
    ],
)
