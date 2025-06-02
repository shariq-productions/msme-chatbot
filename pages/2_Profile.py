import streamlit as st
import requests

# Replace with your actual endpoints
PROFILE_URL = "http://35.154.166.48:8000/admin/viewProfile"
UPDATE_PROFILE_URL = "http://your-api-url.com/update-profile"

st.set_page_config(page_title="View & Update Profile", page_icon="🧾")
st.title("👤 View & Update MSME Profile")

# Check for bearer token
if "bearer_token" not in st.session_state or not st.session_state.bearer_token:
    st.warning("🔐 Please log in first to access this page.")
    st.stop()

# Fetch current profile
try:
    headers = {"Authorization": f"Bearer {st.session_state.bearer_token}"}
    res = requests.get(PROFILE_URL, headers=headers)
    if res.status_code == 200:
        profile_data = res.json()
    else:
        st.error("⚠️ Failed to fetch profile. Please log in again.")
        st.stop()
except Exception as e:
    st.error(f"❌ Error: {e}")
    st.stop()

# --- Display current profile ---
st.subheader("📄 Current Profile Details")
st.write(f"**Enterprise Type:** {profile_data.get('enterprise_type', 'N/A')}")
st.write(f"**Industry:** {profile_data.get('industry_category', 'N/A')}")
st.write(f"**Women-led:** {profile_data.get('women_led', 'N/A')}")
st.write(f"**Social Caste:** {profile_data.get('social_caste', 'N/A')}")
st.write(f"**State:** {profile_data.get('state', 'N/A')}")
st.write(f"**District:** {profile_data.get('district', 'N/A')}")

# --- Update Profile Form ---
st.subheader("📝 Update Enterprise Profile")

with st.form("profile_update_form"):
    enterprise_type = st.text_input("Enterprise Type", value=profile_data.get('enterprise_type', 'N/A'))
    industry_category = st.text_input("Industry Category", value=profile_data.get('industry_category', 'N/A'))
    women_led = st.selectbox("Women-led", ["Yes", "No"], index=0 if profile_data.get('women_led', 'N/A') else 1)
    
    social_caste_options = ["General", "SC", "ST", "OBC", "Minority", "Other"]
    social_caste_value = profile_data.get('social_caste', 'General')
    if social_caste_value not in social_caste_options:
        social_caste_value = social_caste_options[0]
    social_caste = st.selectbox(
        "Social Caste",
        social_caste_options,
        index=social_caste_options.index(social_caste_value)
    )

    state_options = ["Andhra Pradesh", "Telangana", "Karnataka", "Maharashtra", "Tamil Nadu", "Kerala", "Delhi", "Other"]
    state_value = profile_data.get('state', 'Andhra Pradesh')
    if state_value not in state_options:
        state_value = state_options[0]
    state = st.selectbox(
        "State",
        state_options,
        index=state_options.index(state_value)
    )
    district = st.text_input("District", value=profile_data.get('district', 'N/A'))

    submitted = st.form_submit_button("Update Profile")

# --- Handle Submission ---
if submitted:
    payload = {
        "enterprise_type": enterprise_type,
        "industry_category": industry_category,
        "women_led": women_led == "Yes",
        "social_caste": social_caste,
        "state": state,
        "district": district,
    }

    try:
        res = requests.post(UPDATE_PROFILE_URL, json=payload, headers=headers)
        if res.status_code == 200:
            st.success("✅ Profile updated successfully.")
            st.experimental_rerun()
        else:
            st.error(f"❌ Failed to update: {res.json().get('detail', 'Unknown error')}")
    except Exception as e:
        st.error(f"❌ Error: {e}")
