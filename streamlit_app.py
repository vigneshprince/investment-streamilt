import streamlit as st

pg=st.navigation([st.Page('pages/auth.py'),st.Page('pages/main_page.py')],position="hidden")
pg.run()