from datetime import datetime,date,timedelta
import os
import string
import pandas as pd
import streamlit as st
import streamlit_antd_components as sac
import firebase_admin
from firebase_admin import credentials,firestore,storage
from google.cloud.firestore_v1.base_query import FieldFilter
from streamlit_free_text_select import st_free_text_select
import random
import json
from dateutil.relativedelta import relativedelta
import streamlit as st
from streamlit_google_auth_handler import Authenticate

cola,colb=st.columns([1,1],vertical_alignment="bottom")
cola.header("Investment Tracker")
if colb.button("Logout"):
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
    authenticator.logout()
    st.switch_page('pages/auth.py')

def get_filename_and_extension(file_path):
  filename, extension = os.path.splitext(file_path)
  filename = os.path.basename(filename)  # Get only the filename, not the entire path
  return filename, extension

def calculate_cumulative_interest():
    principal, rate, time, n =  st.session_state['inv_amount_ip'] or 0, st.session_state['percent_ip']/100,st.session_state['mat_date_inp'].year - st.session_state['inv_date_inp'].year,1
    st.session_state["mat_amount_ip"]=int(principal * (1 + (rate / n)) ** (n * time))

def upload_to_firebase():
    inv_docs=[]
    for file_obj in uploaded_files:
        blob_name=file_obj.name
        if bucket.blob(blob_name).exists():
            random_string = ''.join(random.choices(string.ascii_lowercase, k=4))
            name,ext=get_filename_and_extension(blob_name)
            blob_name = f"{name}_{random_string}.{ext}"

        blob = bucket.blob(blob_name) # Use the original file path as the blob name
        blob.upload_from_string(
            file_obj.read(),
            content_type=file_obj.type)
        inv_docs.append(blob_name)

    if st.session_state['inv_amount_ip'] < 10 :
        st.error("Invalid investment amount")
    collection.document().set({
        "id":inv_id,
        "Name":inv_name_ip,
        "type":type_ip,
        "person":person_ip,
        "inv_amount_ip": st.session_state['inv_amount_ip'],
        "mat_amount_ip":st.session_state['mat_amount_ip'],
        "inv_date_inp":datetime.combine(st.session_state['inv_date_inp'] , datetime.min.time()),
        "mat_date_inp":datetime.combine(st.session_state['inv_date_inp'] , datetime.min.time()),
        "notes":notes,
        "docs":inv_docs
    })


@st.cache_data
def generate_random_investment_data(num_records=20):
    data = []
    investment_names = ["Stock A", "Bond B", "Mutual Fund C", "ETF D", "Real Estate E"]

    for _ in range(num_records):
        investment_name = random.choice(investment_names)
        invest_date = date(
            year=random.randint(2015, 2023),
            month=random.randint(1, 12),
            day=random.randint(1, 28),
        )
        maturity_date = invest_date + timedelta(days=random.randint(365, 365 * 5))  # 1 to 5 years maturity
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

    return data

def process_dates(data):
    for k,v in data.items():
        if isinstance(v, datetime):
            data[k]=v.date()
    return data

@st.cache_data
def get_firebase_data():
    data=[]
    for doc in collection.stream():
        data.append(process_dates(doc.to_dict()))
    return data
    

@st.cache_data
def get_inv_names():
    return list({x['investment_name'] for x in json_data})

json_data = generate_random_investment_data()
inv_names= get_inv_names()

months = ["","January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December" ]

@st.cache_resource
def firebase_clients():
    cred = credentials.Certificate(dict(st.secrets["firebase"]))
    firebase_admin.initialize_app(cred,{'storageBucket':"mystodocs.appspot.com"})
    return firestore.client().collection("investments") , storage.bucket()

collection,bucket=firebase_clients()
# json_data = get_firebase_data()

def clear_Text():
    st.session_state.srch=""
    st.session_state.yearsel=None
    st.session_state.monthsel=""

def toggler():
    st.session_state['toggle_button']=not st.session_state['toggle_button']

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

@st.dialog("New investment")
def newinv():
    pass

def change_maturity_date():
    if st.session_state['yrs_inp']!="Inf":
        st.session_state['mat_date_inp']=st.session_state['inv_date_inp'] + relativedelta(years=st.session_state['yrs_inp'])
    else:
        st.session_state['mat_date_inp']=date(2099,1,1)


type_ip=sac.segmented(
items=[
    sac.SegmentedItem(label='RD'),
    sac.SegmentedItem(label='FD'),
], label='', align='center')
person_ip=sac.segmented(
items=[
        sac.SegmentedItem(label=x) for x in ["Vignesh","Mom","Dad","Shivani"]
    ]
, label='', align='center'
)
inv_id=st.text_input(label="Investment ID",placeholder="Enter Investment ID")
inv_name_ip = st_free_text_select(
        options=inv_names,
        label="Investment Name",
        index=None,
        placeholder="Select an Investment or Enter new name",
        disabled=False,
        delay=300,
        label_visibility="visible",
    )
st.date_input(label="Investment Date",key="inv_date_inp")
col7,col8 = st.columns([5,1],vertical_alignment="bottom")
if "mat_date_inp" not in st.session_state:
    st.session_state['mat_date_inp']=date.today() + relativedelta(years=5)

with col7:
    st.date_input(label="Maturity Date",value=st.session_state['mat_date_inp'],key="mat_date_inp")
with col8:
    st.selectbox(label="Yrs",index=5,options=["Inf"]+list(range(1,15)),on_change=change_maturity_date,key="yrs_inp")

if "inv_amount_ip" not in st.session_state:
        st.session_state["inv_amount_ip"] = None

st.number_input("Investment Amount",key="inv_amount_ip",step=500,value=st.session_state["inv_amount_ip"])
col9,col10,col11 = st.columns([1,5,1],vertical_alignment="bottom")

if "percent_ip" not in st.session_state:
        st.session_state["percent_ip"] = 8

if "mat_amount_ip" not in st.session_state:
        st.session_state["mat_amount_ip"] = None
        calculate_cumulative_interest()

col9.number_input("Percent",step=1,key="percent_ip",value=st.session_state["percent_ip"])
col10.number_input("Maturity Amount",step=500,key="mat_amount_ip",value=st.session_state["mat_amount_ip"])
col11.button("Compound interest",on_click=calculate_cumulative_interest)

notes=st.text_area("Additional notes")

uploaded_files = st.file_uploader(
    "Upload investment proofs",type=["pdf","jpeg","png","jpg"] ,accept_multiple_files=True
)
st.button('Submit',on_click=upload_to_firebase)


col3, col4, col5,col6 = st.columns([1,1,1,1],vertical_alignment="bottom")
with col3:
    if "toggle_button" not in st.session_state:
        st.session_state["toggle_button"] = False

    if st.session_state["toggle_button"]:
        st.button('Maturity Date :material/Anchor:',on_click=toggler)
    else:
        st.button('Investment Date :material/Anchor:',on_click=toggler)

with col4:
    st.number_input("Year",value=None,step=1,key="yearsel")
with col5:
    st.selectbox("Month",months,key="monthsel")

with col6:
    if st.button('New :material/Add:'):newinv()


st.data_editor(pd.DataFrame(json_data),use_container_width=True)



