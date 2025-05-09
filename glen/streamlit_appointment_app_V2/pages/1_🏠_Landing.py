import streamlit as st
from auth import check_auth, get_current_user, logout

st.set_page_config(page_title="Home", page_icon="🏠")


# Check authentication
if not st.session_state.get("authenticated", False):
    st.switch_page("main.py")

check_auth()

user = get_current_user()

st.title(f"Welcome to HealthPlus, {user['name']}!")
st.write("""
### Our Services
- **Consultations**: Expert medical advice from our specialists
- **Medical Screenings**: Comprehensive health assessments
- **Preventive Care**: Keep your health on track

Book an appointment today to experience our premium healthcare services.
""")

if st.button("Logout"):
    logout()