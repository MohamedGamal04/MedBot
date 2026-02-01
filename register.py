import streamlit as st
from user import register_user, login_user 
import json

st.set_page_config(page_title="User Auth System", page_icon="🔐")
st.title("Welcome to the Portal")

tab1, tab2 = st.tabs(["Login", "Register"])

# --- LOGIN TAB ---
with tab1:
    st.header("Login to Your Account")
    chainlit_url = "http://localhost:8000/login"
    st.link_button("🚀 Open Chat", chainlit_url, use_container_width=True)

    
# --- REGISTER TAB ---
with tab2:
    st.header("Create Account")
    with st.form("register_form"):
        col1, col2 = st.columns(2)
        with col1:
            f_name = st.text_input("First Name")
            u_name = st.text_input("Username*")
            u_email = st.text_input("Email*")
        with col2:
            l_name = st.text_input("Last Name")
            u_age = st.number_input("Age", min_value=0, max_value=120, step=1)
            u_password = st.text_input("Password*", type="password")
        
        submit_reg = st.form_submit_button("Register")

        if submit_reg:
            if not u_name or not u_email or not u_password:
                st.warning("Please fill in all required fields.")
            else:
                try:
                    register_user(f_name, l_name, u_name, u_email, u_age, u_password)
                    st.success("Account created successfully! Please head to the Login tab.")
                except ValueError as e:
                    st.error(f"Error: {e}")
                except Exception as e:
                    st.error("An unexpected error occurred.")