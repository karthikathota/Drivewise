import streamlit as st
import requests
import uuid

API_URL = "http://127.0.0.1:8000/recommend"

st.set_page_config(page_title="DriveWise", page_icon="🚗", layout="wide")


# ===============================
# SESSION STATE INIT
# ===============================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())


# ===============================
# BACKEND CALL
# Client timeout: 60s
# Server timeout: 45s (agents.py) — server always responds before client cuts off
# ===============================

def call_backend(query: str) -> str:
    try:
        response = requests.post(
            API_URL,
            json={
                "question": query,
                "session_id": st.session_state.session_id
            },
            timeout=60  # Must stay > server-side asyncio.wait_for timeout (45s)
        )
        if response.status_code == 200:
            return response.json().get("answer", "No answer returned.")
        return f"⚠️ Backend returned error {response.status_code}. Please try again."

    except requests.exceptions.ConnectionError:
        return (
            "❌ Cannot reach the backend. "
            "Make sure the FastAPI server is running:\n\n"
            "```\nuvicorn main:app --reload --port 8000\n```"
        )
    except requests.exceptions.Timeout:
        return (
            "⏱️ The request timed out. "
            "The server is taking longer than expected — please try again."
        )
    except Exception as e:
        return f"❌ Unexpected error: {e}"


# ===============================
# HEADER
# ===============================

st.title("🚘 DriveWise AI Advisor")
st.caption("Your premium vehicle recommendation assistant — powered by AI")
st.divider()


# ===============================
# DISPLAY CHAT HISTORY
# ===============================

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# ===============================
# CHAT INPUT
# ===============================

user_input = st.chat_input("Tell me your budget, needs, or preferences...")

if user_input:
    # 1. Store + render user message immediately
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 2. Call backend and render response in assistant bubble
    with st.chat_message("assistant"):
        with st.spinner("Finding the best vehicles for you..."):
            response = call_backend(user_input)
        st.markdown(response)

    # 3. Store assistant message
    st.session_state.messages.append({"role": "assistant", "content": response})

    # No st.rerun() here — causes a double-render loop.
    # Streamlit re-renders naturally after this block completes.


# ===============================
# SIDEBAR
# ===============================

with st.sidebar:
    st.markdown("### 🚗 DriveWise")
    st.markdown("**Try asking:**")
    st.markdown(
        "- *Family SUV around $50,000*\n"
        "- *Eco-friendly car under $40k*\n"
        "- *Best EVs between $30k and $60k*\n"
        "- *Affordable crossover for a family*\n"
        "- *Hybrid SUV for a family under $55k*"
    )
    st.divider()

    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()

    st.markdown("---")
    st.caption(f"Session: `{st.session_state.session_id[:8]}...`")