from datetime import datetime,date,timedelta
import os
import string
import pandas as pd
import streamlit as st
import streamlit_antd_components as sac
from google.cloud.firestore_v1.base_query import FieldFilter
from streamlit_free_text_select import st_free_text_select
import random
import json
from dateutil.relativedelta import relativedelta
import streamlit as st
from streamlit_google_auth_handler import Authenticate
from firebase_admin import firestore,storage
import numpy as np
from utils import *
from consts import *
# if not st.session_state.get('connected',False):
#     st.switch_page('pages/auth.py')

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
    if type_ip=='FD':
        principal, rate, time, n =  st.session_state['inv_amount_ip'] or 0, st.session_state['percent_ip']/100,st.session_state['mat_date_inp'].year - st.session_state['inv_date_inp'].year,1
        st.session_state["mat_amount_ip"]=int(principal * (1 + (rate / n)) ** (n * time))
    else:
        principal, rate, n =  st.session_state['inv_amount_ip'] or 0, st.session_state['percent_ip']/100,RD_options[st.session_state['freq']]
        rate_div=rate/n
        total_frequency=get_duration(st.session_state['inv_date_inp'],st.session_state['mat_date_inp'],st.session_state['freq'])
        st.session_state["mat_amount_ip"]= principal * (((1 + rate_div) ** total_frequency - 1) / rate_div) * (1 + rate_div)

def calculate_cumulative_interest_1(r,till_date):
    till_date=min(datetime.combine(till_date, datetime.min.time()) ,r['maturity_date'])
    if r['type']=='FD':
        principal, rate, time, n =  r['investment_value'], r['percent_return']/100, till_date.year - r['invest_date'].year,1
        return int(principal * (1 + (rate / n)) ** (n * time))
    else:
        principal, rate, n =  r['investment_value'], r['percent_return']/100 ,RD_options[r['freq']]
        rate_div=rate/n
        total_frequency=get_duration(r['invest_date'],till_date,r['freq'])

        return principal * (((1 + rate_div) ** total_frequency - 1) / rate_div) * (1 + rate_div)


def curr_invest_value(r,till_date):
    till_date=min(datetime.combine(till_date, datetime.min.time()),r['maturity_date'])
    total_frequency=get_duration(r['invest_date'],till_date,r['freq'])
    return r['investment_value'] * total_frequency



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
        "investment_name":inv_name_ip,
        "type":type_ip,
        "person":person_ip,
        "investment_value": st.session_state['inv_amount_ip'],
        "maturity_value":st.session_state['mat_amount_ip'],
        "invest_date":datetime.combine(st.session_state['inv_date_inp'] , datetime.min.time()),
        "matrurity_date":datetime.combine(st.session_state['inv_date_inp'] , datetime.min.time()),
        "percent_return": st.session_state['percent_ip'],
        "notes":notes,
        "docs":inv_docs,
        "closed":False
    })


@st.cache_data
def generate_random_investment_data(num_records=20):
    data = []
    investment_names = ["Stock A", "Bond B", "Mutual Fund C", "ETF D", "Real Estate E"]

    for _ in range(num_records):
        investment_name = random.choice(investment_names)
        type = random.choice(['RD',"FD"])
        person=random.choice(["All","Vignesh","Mom","Dad","Shivani"])
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
            "invest_date": invest_date,
            "type":type,
            "person":person,
            "maturity_date": maturity_date,
            "percent_return": percent_return,
            "investment_value": investment_value,
            "maturity_value": maturity_value,
            "freq":freq,
        })
        df=pd.DataFrame(data)

    return df

inv_data = generate_random_investment_data()
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
    return list(set(inv_data['investment_name']))



@st.cache_data
def filter_investments(tgl_button, year,month, srch_txt ):
    filtered_df=inv_data.copy(deep=True)

    end_date=date.today()

    
    if tgl_button:
        date_col="maturity_date"
        if year and month:
            end_date=date(year,month,30)
        elif year:
            end_date=date(year,12,31)
    else:
        date_col="invest_date"
    
    filtered_df['maturity_value'] = np.where(filtered_df['maturity_date'].dt.year== 2099,\
                                              filtered_df.apply(lambda r:calculate_cumulative_interest_1(r,end_date), axis=1),\
                                                filtered_df['maturity_value'])
    
    filtered_df['investment_value'] =np.where(filtered_df['type'] == "RD", filtered_df.apply(lambda r:curr_invest_value(r,end_date),axis=1),filtered_df['investment_value'])

    if srch_txt:
        filtered_df = filtered_df[filtered_df['investment_name'].str.lower().str.contains(srch_txt)]

    if date_col=="maturity_date":
        common_data=filtered_df[filtered_df[date_col].dt.year==2099].copy(deep=True)

    if year:
        filtered_df = filtered_df[filtered_df[date_col].dt.year == year]
    if month:
        filtered_df = filtered_df[filtered_df[date_col].dt.month == months.index(month)]
    if date_col=="maturity_date":
        return pd.concat([filtered_df,common_data])
    return filtered_df


inv_names= get_inv_names()


collection, bucket = firestore.client().collection("investments"), storage.bucket()
# json_data = get_firebase_data()

def clear_Text():
    st.session_state.srch=""
    st.session_state.yearsel=None
    st.session_state.monthsel=""

def toggler():
    st.session_state['toggle_button']=not st.session_state['toggle_button']

col1, col2 = st.columns([2,2],vertical_alignment="bottom")

with col1:
    st.text_input(label="Filter",placeholder="Search",key="srch")

with col2:
    st.button("Clear :material/clear:",on_click=clear_Text)


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

def add_inv():

    type_ip=sac.segmented(
    items=[
        sac.SegmentedItem(label='FD'),
        sac.SegmentedItem(label='RD'),
    ], label='', align='center')

    person_ip=sac.segmented(
    items=[
            sac.SegmentedItem(label=x) for x in people
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
    if type_ip=="FD":
        col7,col8 = st.columns([3,1],vertical_alignment="bottom")
        if "mat_date_inp" not in st.session_state:
            st.session_state['mat_date_inp']=date.today() + relativedelta(years=5)

        with col7:
            st.date_input(label="Maturity Date",key="mat_date_inp")
        with col8:
            st.selectbox(label="Yrs",index=5,options=["Inf"]+list(range(1,15)),on_change=change_maturity_date,key="yrs_inp")
    else:
        col7,col8,col_rd = st.columns([3,1,1],vertical_alignment="bottom")
        if "mat_date_inp" not in st.session_state:
            st.session_state['mat_date_inp']=date.today() + relativedelta(years=5)

        with col7:
            st.date_input(label="Maturity Date",key="mat_date_inp")
        with col8:
            st.selectbox(label="Yrs",index=5,options=["Inf"]+list(range(1,15)),on_change=change_maturity_date,key="yrs_inp")
        with col_rd:
            st.selectbox(label="Frequency",index=2,options=RD_options,key="freq")



    st.number_input("Investment Amount",key="inv_amount_ip",step=500)
    col9,col10,col11 = st.columns([1,2,1],vertical_alignment="bottom")

    if "percent_ip" not in st.session_state:
            st.session_state["percent_ip"] = 8

    col9.number_input("Percent",step=1,key="percent_ip")
    col10.number_input("Maturity Amount",step=500,key="mat_amount_ip")
    col11.button("CP interest",on_click=calculate_cumulative_interest)

    notes=st.text_area("Additional notes")

    uploaded_files = st.file_uploader(
        "Upload investment proofs",type=["pdf","jpeg","png","jpg"] ,accept_multiple_files=True
    )
    colx, coly, colz = st.columns([5,3,5])

    coly.button('Submit',on_click=upload_to_firebase)


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
    if st.button('New :material/Add:'):newinv()


inv_data_filtered = filter_investments(st.session_state["toggle_button"] , st.session_state["yearsel"], st.session_state["monthsel"],st.session_state["srch"])


st.data_editor(inv_data_filtered,use_container_width=True)



