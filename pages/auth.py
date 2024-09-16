import streamlit as st
from utils import get_auth_obj

authenticator=get_auth_obj()
authenticator.check_authentication()
if not st.session_state['connected']:
    authenticator.login()
else:
    st.switch_page("pages/main_page.py")

