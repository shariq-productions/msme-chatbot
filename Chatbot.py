import streamlit as st
import requests

BASE_URL = "http://127.0.0.1:8000"  # change this to your backend base URL

st.set_page_config(page_title="Chatbot", page_icon="💬")
st.title("💬 MSME Chatbot")
st.caption("🧠 Powered by your backend & OpenAI")

# Store session and messages in Streamlit session_state
if "selected_session" not in st.session_state:
    st.session_state.selected_session = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# -------- Sidebar --------
with st.sidebar:
    st.header("📁 Sessions")
    new_session_name = st.text_input("Create New Session", key="new_session_input")
    if st.button("➕ Create Session"):
        if new_session_name:
            try:
                res = requests.post(f"{BASE_URL}/session/createSession", json={"session_name": new_session_name})
                if res.status_code == 200:
                    st.success("✅ Session created!")
                    st.rerun()
                else:
                    st.error("❌ Failed to create session.")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("⚠️ Please enter a session name.")

    # Fetch and list all sessions
    try:
        res = requests.get(f"{BASE_URL}/session/viewAllSessions")
        if res.status_code == 200:
            try:
                session_list = res.json()  # This line was crashing
            except ValueError:
                session_list = []  # Assumes: ["session1", "session2"]
            if not session_list:
                st.info("📝 No sessions found. Create a session to get started!")
            else:
                for session_name in session_list:
                    if st.button(session_name):
                        st.session_state.selected_session = session_name
                        # Fetch messages for this session
                        try:
                            chat_res = requests.get(f"{BASE_URL}/chats/{session_name}")
                            if chat_res.status_code == 200:
                                st.session_state.messages = chat_res.json()
                                st.rerun()
                            else:
                                st.error("❌ Failed to load chats.")
                        except Exception as e:
                            st.error(f"Error: {e}")
        else:
            st.error("❌ Could not fetch sessions.")
    except Exception as e:
        st.error(f"Error fetching sessions: {e}")


# -------- Chat Display --------
if not st.session_state.selected_session:
    st.info("ℹ️ Select a session from the sidebar to begin.")
    st.stop()

for msg in st.session_state.messages:
    role = "user" if msg.get("type") == "user" else "assistant"
    st.chat_message(role).write(msg.get("message", ""))

# -------- Chat Input --------
if prompt := st.chat_input("Ask something..."):
    if not st.session_state.selected_session:
        st.warning("⚠️ Select a session first.")
        st.stop()

    user_msg = {"type": "user", "message": prompt}
    st.session_state.messages.append(user_msg)
    st.chat_message("user").write(prompt)

    # Send to backend for response
    try:
        res = requests.post(
            f"{BASE_URL}/chats/{st.session_state.selected_session}",
            json={"message": prompt}
        )
        if res.status_code == 200:
            bot_msg = res.json()  # e.g., {"type": "bot", "message": "..."}
            st.session_state.messages.append(bot_msg)
            st.chat_message("assistant").write(bot_msg["message"])
        else:
            st.error("❌ Bot failed to respond.")
    except Exception as e:
        st.error(f"Error: {e}")
