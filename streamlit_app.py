from datetime import datetime,date
import pandas as pd
import streamlit as st
import streamlit_antd_components as sac
import firebase_admin
from firebase_admin import credentials,firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from streamlit_date_picker import date_picker, PickerType

import random
import datetime
import json

st.set_page_config(layout="wide")

@st.cache_data
def generate_random_investment_data(num_records=20):
    data = []
    investment_names = ["Stock A", "Bond B", "Mutual Fund C", "ETF D", "Real Estate E"]

    for _ in range(num_records):
        investment_name = random.choice(investment_names)
        invest_date = datetime.date(
            year=random.randint(2015, 2023),
            month=random.randint(1, 12),
            day=random.randint(1, 28),
        )
        maturity_date = invest_date + datetime.timedelta(days=random.randint(365, 365 * 5))  # 1 to 5 years maturity
        percent_return = round(random.uniform(-0.1, 0.3), 2)  # -10% to 30% return
        investment_value = round(random.uniform(1000, 10000), 2)
        maturity_value = round(investment_value * (1 + percent_return), 2)

        data.append({
            "investment_name": investment_name,
            "invest_date asdasd ": invest_date.strftime("%Y-%m-%d"),
            "maturity_date": maturity_date.strftime("%Y-%m-%d"),
            "percent_return": percent_return,
            "investment_value": investment_value,
            "maturity_value": maturity_value
        })

    return json.dumps(data, indent=4)

# Generate and print the JSON data
json_data = generate_random_investment_data()

months = ["","January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December" ]

sample_Data=[["sriram",date.today(),date]]
@st.cache_resource
def firebase_coll():
    cred = credentials.Certificate(dict(st.secrets["firebase"]))
    firebase_admin.initialize_app(cred)
    return firestore.client().collection("investments")

collection=firebase_coll()

def clear_Text():
    st.session_state.srch=""
    st.session_state.yearsel=None
    st.session_state.monthsel=""

col1, col2 = st.columns([5,2],vertical_alignment="bottom")

with col1:
    st.text_input(label="Filter",placeholder="Search",key="srch")

with col2:
    st.button("Clear Filters :material/clear:",on_click=clear_Text)


selected=sac.chip(
            items=[
                sac.ChipItem(label=x) for x in ["All","Vignesh","Mom","Dad","Shivani"]
            ], label='', index=[0], align='center', radius='md', multiple=False
        )


col3, col4, col5 = st.columns([1,1,2],vertical_alignment="bottom")
with col3:
    st.button("Investment Date :material/Anchor:",key="test")
with col4:
    st.number_input("Year",value=None,step=1,key="yearsel")
with col5:
    st.selectbox("Month",months,key="monthsel")

st.data_editor(pd.read_json(json_data),use_container_width=True)



