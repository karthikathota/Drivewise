import streamlit as st
import requests
from datetime import datetime

# =====================================================
# CONFIG
# =====================================================

API_URL = "http://127.0.0.1:8000/recommend"

st.set_page_config(
    page_title="DriveWise | AI Vehicle Advisor",
    page_icon="🚗",
    layout="wide",
)

# =====================================================
# SESSION STATE INIT
# =====================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_query" not in st.session_state:
    st.session_state.pending_query = None

# =====================================================
# SAFE BACKEND CALL
# =====================================================

def safe_backend_call(query: str):
    try:
        response = requests.post(
            API_URL,
            json={"question": query},
            timeout=30
        )

        if response.status_code != 200:
            return False, f"Backend returned status {response.status_code}"

        data = response.json()

        if "answer" not in data:
            return False, "Invalid backend response format."

        return True, data["answer"]

    except requests.exceptions.Timeout:
        return False, "Backend request timed out."
    except requests.exceptions.ConnectionError:
        return False, "Cannot connect to backend."
    except Exception as e:
        return False, str(e)

# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:
    st.title("🚗 DriveWise")
    st.caption("Multi-Agent Vehicle Recommendation System")

    st.markdown("---")

    st.subheader("💡 Example Queries")

    example_queries = [
        "Suggest 3 electric cars under $60,000",
        "Family friendly SUV between 50k and 80k",
        "Best hybrid cars for city driving",
        "Affordable EVs with good range",
    ]

    for q in example_queries:
        if st.button(q, use_container_width=True):
            st.session_state.pending_query = q

    st.markdown("---")

    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pending_query = None

    st.markdown("---")
    st.caption("Final Year Project • DriveWise")

# =====================================================
# MAIN HEADER
# =====================================================

st.markdown(
    """
    <h1 style='margin-bottom: 0;'>🚘 DriveWise AI Advisor</h1>
    <p style='color: gray; margin-top: 4px;'>
        Ask questions about vehicles. Our multi-agent AI handles the rest.
    </p>
    """,
    unsafe_allow_html=True
)

st.divider()

# =====================================================
# EMPTY STATE
# =====================================================

if len(st.session_state.messages) == 0:
    st.info(
        "👋 Welcome to DriveWise!\n\n"
        "Use the chat below or click an example from the sidebar."
    )

# =====================================================
# DISPLAY CHAT
# =====================================================

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# =====================================================
# CHAT INPUT
# =====================================================

user_input = st.chat_input("Type your vehicle query here...")

# Handle manual input
if user_input:
    st.session_state.pending_query = user_input

# Handle example-triggered input
if st.session_state.pending_query:

    query = st.session_state.pending_query
    st.session_state.pending_query = None

    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": query,
        "time": datetime.now()
    })

    with st.chat_message("user"):
        st.markdown(query)

    # Assistant response
    with st.chat_message("assistant"):
        with st.spinner("Analyzing your request..."):
            success, result = safe_backend_call(query)

            if success:
                st.markdown(result)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result,
                    "time": datetime.now()
                })
            else:
                st.error(f"❌ {result}")
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"Error: {result}",
                    "time": datetime.now()
                })

# =====================================================
# FOOTER
# =====================================================

st.divider()
st.caption("DriveWise • Multi-Agent AI • Electric & Hybrid Recommendations")
