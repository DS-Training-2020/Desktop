import streamlit as st
from auth import check_auth

st.set_page_config(
    page_title="HealthPlus Appointments",
    page_icon="🏥",
    layout="wide"
)

def main():
    if not st.session_state.get("authenticated", False):
        check_auth()
    else:
        # Redirect to landing page if already authenticated
        st.switch_page("pages/1_🏠_Landing.py")

if __name__ == "__main__":
    main()