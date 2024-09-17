import streamlit as st
import firebase_admin
st.set_page_config(layout="wide")

@st.cache_resource
def firebase_clients():
    cred = firebase_admin.credentials.Certificate(dict(st.secrets["firebase"]))
    firebase_admin.initialize_app(cred,{'storageBucket':"mystodocs.appspot.com"})
firebase_clients()

pg=st.navigation([st.Page('auth.py'),st.Page('main_page.py')],position="hidden")
pg.run()