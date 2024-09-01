
import streamlit as st
from streamlit_google_auth_handler import Authenticate

authenticator = Authenticate(
    secret_credentials_path={
        "web": {
            "client_id": st.secrets['cid'],
            "client_secret": st.secrets['csecret'],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    },
    cookie_name='streamlit_auth',
    cookie_key='streamlit_auth_keys',
    redirect_uri='http://localhost:8501/',
)

authenticator.check_authentification()

if  not st.session_state['connected']:
    authenticator.login()
else:
    st.switch_page("pages/main_page.py")

