import streamlit as st
from database import verify_user, register_user

def signup():
    st.title("Sign Up")
    
    with st.form("signup_form"):
        name = st.text_input("Full Name", key="signup_name")
        username = st.text_input("Username", key="signup_username")
        password = st.text_input("Password", type="password", key="signup_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm")
        
        submitted = st.form_submit_button("Sign Up")
        
        if submitted:
            if password != confirm_password:
                st.error("Passwords don't match!")
                return
                
            if not all([name, username, password]):
                st.error("Please fill all fields!")
                return
                
            success = register_user(username, name, password)
            if success:
                st.success("Registration successful! Please login.")
                st.session_state["show_signup"] = False
                st.rerun()
            else:
                st.error("Username already exists!")

def login():
    st.title("Login")
    
    if st.button("Don't have an account? Sign up", key="go_to_signup"):
        st.session_state["show_signup"] = True
        st.rerun()
        return
    
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    
    if st.button("Login", key="login_button"):
        user = verify_user(username, password)
        if user:
            st.session_state["user"] = user
            st.session_state["authenticated"] = True
            st.session_state["current_page"] = "Home"  # Add this line
            st.success("Logged in successfully!")
            st.switch_page("pages/1_🏠_Landing.py")  # Redirect to landing page
        else:
            st.error("Invalid username or password")

def auth_flow():
    if st.session_state.get("show_signup", False):
        signup()
        if st.button("Already have an account? Login", key="go_to_login"):
            st.session_state["show_signup"] = False
            st.rerun()
    else:
        login()

def logout():
    if "user" in st.session_state:
        del st.session_state["user"]
    st.session_state["authenticated"] = False
    st.success("Logged out successfully!")
    st.rerun()

def check_auth():
    if not st.session_state.get("authenticated", False):
        auth_flow()
        st.stop()

def get_current_user():
    return st.session_state.get("user", None)