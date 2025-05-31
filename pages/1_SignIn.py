import streamlit as st
import requests

BASE_URL = "http://127.0.0.1:8000"  # Replace with your actual API base URL

st.set_page_config(page_title="Auth App", page_icon="🔐")

# -------- Session Setup -------- #
if "bearer_token" not in st.session_state:
    st.session_state.bearer_token = None

if "show_signup" not in st.session_state:
    st.session_state.show_signup = False


# -------- Helper Functions -------- #
def login_user(email, password):
    try:
        res = requests.post(f"{BASE_URL}/user/login", data={"username": email, "password": password})
        if res.status_code == 201:
            token = res.json()["access_token"]
            st.session_state.bearer_token = token
            st.success("Login successful!")
            st.session_state["rerun_trigger"] = not st.session_state.get("rerun_trigger", False)
        else:
            st.error(res.json().get("detail", "Login failed."))
    except Exception as e:
        st.error(f"Error: {e}")


def signup_user(data, profile_data):
    try:
        res = requests.post(f"{BASE_URL}/user/signUp?company_id=10", json=data)
        if res.status_code == 201:
            st.success("Signup successful! Please log in.")
            login_user(data["email"], data["password"])
        else:
            st.error(res.json().get("detail", "Signup failed."))

        headers = {
            "Authorization": f"Bearer {st.session_state.get('bearer_token', '')}"
        }
        res = requests.post(f"{BASE_URL}/admin/uploadProfile", json=profile_data, headers=headers)
        if res.status_code == 200:
            st.success("Signup successful! Please log in.")
            st.session_state.show_signup = False
        else:
            st.error(res.json().get("detail", "Signup failed."))
    except Exception as e:
        st.error(f"Error: {e}")


# -------- Main App -------- #
st.title("🧑‍💻 Auth App")

if st.session_state.bearer_token:
    st.success("✅ You are already logged in.")
    if st.button("Logout"):
        st.session_state.bearer_token = None
        st.session_state["rerun_trigger"] = not st.session_state.get("rerun_trigger", False)

else:
    if not st.session_state.show_signup:
        st.subheader("🔐 Login")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        login = st.button("Login")

        if login:
            login_user(email, password)

        st.markdown("Don't have an account? [Sign up here](#)", unsafe_allow_html=True)
        if st.button("Go to Signup"):
            st.session_state.show_signup = True

    else:
        st.subheader("📝 Sign Up")
        name = st.text_input("Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone Number")
        password = st.text_input("Password", type="password")

        enterprise_type = st.selectbox("Enterprise Type", ["Small", "Medium", "Large"])
        industry_category = st.text_input("Industry Category")
        women_led = st.selectbox("Women-led", ["Yes", "No"])
        social_caste = st.selectbox("Social Caste", ["General", "SC", "ST", "OBC", "Minority", "Other"])
        state = st.selectbox("State", [
            "Andhra Pradesh", "Telangana", "Karnataka", "Maharashtra", "Tamil Nadu",
            "Kerala", "Delhi", "Other"
        ])
        district = st.text_input("District")

        signup = st.button("Sign Up")

        if signup:
            signup_data = {
                "name": name,
                "email": email,
                "phone_number": phone,
                "password": password,
            }
            profile_data = {
                "enterprise_type": enterprise_type,
                "industry_category": industry_category,
                "women_led": "Yes" if women_led == "Yes" else "No",
                "social_caste": social_caste,
                "state": state,
                "district": district,
            }
            signup_user(signup_data, profile_data)

        st.markdown("Already have an account? [Log in here](#)", unsafe_allow_html=True)
        if st.button("Back to Login"):
            st.session_state.show_signup = False
