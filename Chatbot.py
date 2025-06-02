import streamlit as st
import requests

BASE_URL = "http://35.154.166.48:8000"  # change this to your backend base URL

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
                headers = {"Authorization": f"Bearer {st.session_state.bearer_token}"}
                res = requests.post(f"{BASE_URL}/session/createSession/{new_session_name}", headers=headers)
                print(res)
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
        headers = {"Authorization": f"Bearer {st.session_state.bearer_token}"}
        res = requests.get(f"{BASE_URL}/session/viewAllSessions", headers=headers)
        if res.status_code == 200:
            try:
                session_list = res.json()  # This line was crashing
            except ValueError:
                session_list = []  # Assumes: ["session1", "session2"]
            if not session_list:
                st.info("📝 No sessions found. Create a session to get started!")
            else:
                for session in session_list:
                    session_id = session.get("session_id")
                    session_name = session.get("session_name", "Unnamed Session")
                    if st.button(session_name, key=session_id):
                        st.session_state.selected_session_id = session_id
                        st.session_state.selected_session_name = session_name
                        # Fetch messages for this session
                        try:
                            chat_res = requests.get(f"{BASE_URL}/chat/getChatHistory?session_id={session_id}")
                            print(chat_res)
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
if "selected_session_id" not in st.session_state or not st.session_state.selected_session_id:
    st.info("ℹ️ Select a session from the sidebar to begin.")
    st.stop()

for msg in st.session_state.messages:
    sender = msg.get("sender", "agent")  # default to agent if missing
    if sender == "user":
        role = "user"
    else:
        role = "assistant"
    st.chat_message(role).write(msg.get("message", ""))

# -------- Chat Input --------
if prompt := st.chat_input("Ask something..."):
    if "selected_session_id" not in st.session_state or not st.session_state.selected_session_id:
        st.warning("⚠️ Select a session first.")
        st.stop()

    user_msg = {"type": "user", "message": prompt}
    st.session_state.messages.append(user_msg)
    st.chat_message("user").write(prompt)

    # Send to backend for response
    try:
        headers = {"Authorization": f"Bearer {st.session_state.bearer_token}"}
        res = requests.post(
            f"{BASE_URL}/chat/query",
            json={"session_id":st.session_state.selected_session_id,"message":prompt},
            headers=headers
        )
        if res.status_code == 200:
            bot_data = res.json()  # {'session_id': ..., 'response': ...}
            bot_msg = {"type": "assistant", "message": bot_data.get("response", "")}
            st.session_state.messages.append(bot_msg)
            st.chat_message("assistant").write(bot_msg["message"])
        else:
            st.error("❌ Bot failed to respond.")
    except Exception as e:
        st.error(f"Error: {e}")
