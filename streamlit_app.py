import streamlit as st
import firebase_admin
from firebase_admin import credentials

st.set_page_config(layout="wide")

@st.cache_resource
def firebase_clients():
    cred = credentials.Certificate(dict(st.secrets["firebase"]))
    firebase_admin.initialize_app(cred,{'storageBucket':"mystodocs.appspot.com"})
firebase_clients()

pg=st.navigation([st.Page('pages/auth.py'),st.Page('pages/main_page.py')],position="hidden")
pg.run()