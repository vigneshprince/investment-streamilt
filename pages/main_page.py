from datetime import datetime,date,timedelta
import urllib.parse
import string
import pandas as pd
import streamlit as st
import streamlit_antd_components as sac
import random
import json
from dateutil.relativedelta import relativedelta
import streamlit as st
from utils import *
from consts import *
from new_inv import add_inv,close_inv

# if not st.session_state.get('connected',False):
#     st.switch_page('pages/auth.py')
@st.dialog("Camera")
def picture_upload():
    picture = st.camera_input("Take a picture")
    
if st.button("Camera"):
    picture_upload()

cola,colb=st.columns([1,1],vertical_alignment="bottom")
cola.header("Investment Tracker")

if colb.button("Logout"):
    
    get_auth_obj().logout()
    st.switch_page('pages/auth.py')


@st.cache_data
def generate_random_investment_data(num_records=20):
    data = []
    investment_names = ["Stock A", "Bond B", "Mutual Fund C", "ETF D", "Real Estate E"]

    for _ in range(num_records):
        investment_name = random.choice(investment_names)
        type = random.choice(['RD',"FD"])
        person=random.choice(people)
        freq=random.choice(list(RD_options))
        invest_date = datetime(
            year=random.randint(2015, 2023),
            month=random.randint(1, 12),
            day=random.randint(1, 28),
        )
        maturity_date = invest_date + timedelta(days=random.randint(365, 365 * 5))  # 1 to 5 years maturity
        percent_return =random.choice(range(5,15))  # -10% to 30% return
        investment_value = round(random.uniform(1000, 10000), 2)
        maturity_value = round(investment_value * (1 + percent_return), 2)

        data.append({
            "investment_name": investment_name,
            "investment_id": ''.join(random.choices(string.ascii_lowercase, k=4)),
            "invest_date": invest_date,
            "type":type,
            "person":person,
            "maturity_date": maturity_date,
            "percent_return": percent_return,
            "investment_value": investment_value,
            "maturity_value": maturity_value,
            "freq":freq,
            "notes": ""
        })
        df=pd.DataFrame(data)

    return df



@st.cache_data
def get_inv_names():
    return list(set(inv_data['investment_name']))


inv_data = get_firebase_data()
inv_names= get_inv_names()

def clear_Text():
    st.session_state.srch=""
    st.session_state.yearsel=None
    st.session_state.monthsel=""
    st.session_state["selected_person"]="All"

def toggler():
    st.session_state['toggle_button']=not st.session_state['toggle_button']

col1, col2 = st.columns([2,2],vertical_alignment="bottom")

with col1:
    st.text_input(label="Filter",placeholder="Search",key="srch")

with col2:
    st.button("Clear :material/clear:",on_click=clear_Text)


sac.chip(
            items=[
                sac.ChipItem(label=x) for x in ["All"]+people
            ], label='', index=[0], align='center', radius='md', multiple=False,key="selected_person"
        )

def change_maturity_date():
    if st.session_state['yrs_inp']!="Inf":
        st.session_state['mat_date_inp']=st.session_state['inv_date_inp'] + relativedelta(years=st.session_state['yrs_inp'])
    else:
        st.session_state['mat_date_inp']=date(2099,1,1)


col3, col4, col5,col6 = st.columns([1,1,1,1],vertical_alignment="bottom")
with col3:
    if "toggle_button" not in st.session_state:
        st.session_state["toggle_button"] = False

    if st.session_state["toggle_button"]:
        st.button('Mat Date :material/Anchor:',on_click=toggler)
    else:
        st.button('Inv Date :material/Anchor:',on_click=toggler)

with col4:
    st.number_input("Year",value=None,step=1,key="yearsel")
with col5:
    st.selectbox("Month",months,key="monthsel")

with col6:
    if st.button('New :material/Add:'):
        existing_data={
            "type_ip":"FD",
            "person_ip":"Maheswari",
            "inv_id_ip":'',
            "inv_name_ip":None,
            "inv_date_ip":date.today(),
            "mat_date_ip":date.today() + relativedelta(years=5),
            "freq_ip":"Monthly",
            "percent_ip":8,
            "yrs_ip":5,
            "inv_amount_ip":5000,
            "mat_amount_ip":0,
            "notes_ip":"",
            "firebase_id":"",
            "docs":[]
        }
        for k in existing_data:
            st.session_state[k] = existing_data[k]
        add_inv(inv_names,types_data.index(st.session_state['type_ip']),people.index(st.session_state['person_ip']))



inv_data_filtered = filter_investments(st.session_state["toggle_button"] , st.session_state["yearsel"], st.session_state["monthsel"],st.session_state["srch"],st.session_state['selected_person'])
inv_data_filtered['test_col']=random.randint(1,1000)

@st.dialog(title="More Info")
def add_info(docs):
    for d in docs:
        st.link_button(urllib.parse.unquote(d), bucket.blob(d).generate_signed_url(
        version="v4",
        expiration=timedelta(minutes=30),  # or a datetime.timedelta object
        method="GET",
    ))

    st.dataframe(st.session_state["add_info"].set_index(st.session_state["add_info"].columns[0]),use_container_width=True)



if 'deditor' in st.session_state:
    for k,v in st.session_state['deditor']['edited_rows'].items():
        for k1 in v:
            if k1=="Edit":
                existing_data={
                "type_ip":inv_data_filtered['type'].iloc[k],
                "person_ip":inv_data_filtered['person'].iloc[k],
                "inv_id_ip":inv_data_filtered['investment_id'].iloc[k],
                "inv_name_ip":inv_data_filtered['investment_name'].iloc[k],
                "inv_date_ip":inv_data_filtered['invest_date'].iloc[k],
                "mat_date_ip":inv_data_filtered['maturity_date'].iloc[k],
                "freq_ip":inv_data_filtered['freq'].iloc[k],
                "percent_ip":inv_data_filtered['percent_return'].iloc[k],
                "yrs_ip":5,
                "inv_amount_ip":inv_data_filtered['investment_value'].iloc[k],
                "mat_amount_ip":inv_data_filtered['maturity_value'].iloc[k],
                "notes_ip":inv_data_filtered['notes'].iloc[k],
                "docs":inv_data_filtered['docs'].iloc[k],
                }
                firebase_id=inv_data_filtered['id'].iloc[k]
                for k in existing_data:
                    st.session_state[k] = existing_data[k]
                add_inv(inv_names,types_data.index(st.session_state['type_ip']),people.index(st.session_state['person_ip']),firebase_id)

            elif k1=="Select":
                docs=inv_data_filtered['docs'].iloc[k]
                st.session_state["add_info"]= pd.DataFrame(list(inv_data_filtered[['type', 'person', 'investment_id', 'investment_name', 'invest_date', 'maturity_date', 'freq', 'percent_return', 'investment_value', 'maturity_value', 'notes',]].iloc[k].items()), columns=['Category', 'Value'])
                add_info(docs)
            
            elif k1=="Close":
                st.session_state["close_inv"]= pd.DataFrame(list(inv_data_filtered[['person', 'investment_id', 'investment_name', 'invest_date', 'maturity_date', 'investment_value', 'maturity_value']].iloc[k].items()), columns=['Category', 'Value'])
                close_inv(inv_data_filtered['id'].iloc[k])



st.data_editor(inv_data_filtered,use_container_width=True,hide_index=True,
             column_config={
        "test_col":None,
        "freq":None,
        "investment_id":None,
        "type":None,
        "percent_return":None,
        "notes":None,
        "docs":None,
        "invest_date": st.column_config.DateColumn(
            format="DD/MM/YYYY",
            step=1,
        ),
        "maturity_date": st.column_config.DateColumn(
            format="DD/MM/YYYY",
            step=1,
        ),
        "id":None
    },
    key="deditor",
             )


