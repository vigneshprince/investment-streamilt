import os
from google.cloud.firestore_v1.base_query import FieldFilter
from datetime import datetime,date
import numpy as np
from datetime import datetime
from firebase_admin import firestore,storage
import streamlit as st
from streamlit_google_auth_handler import Authenticate
from consts import *
import pandas as pd


def curr_invest_value(r,till_date):
    till_date=min(datetime.combine(till_date, datetime.min.time()),r['maturity_date'])
    total_frequency=get_duration(r['invest_date'],till_date,r['freq'])
    return r['investment_value'] * total_frequency


def get_auth_obj():
    return Authenticate(
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
    # redirect_uri='https://vigneshprince-investment-streamilt-streamlit-app-bb937a.streamlit.app/',
)

def get_filename_and_extension(file_path):
  filename, extension = os.path.splitext(file_path)
  filename = os.path.basename(filename)  # Get only the filename, not the entire path
  return filename, extension

def calculate_cumulative_interest(inv_amount,percent,mat_date,inv_date,freq,type):
    if type=='FD':
        principal, rate, time, n =  inv_amount or 0, percent/100,mat_date.year - inv_date.year,1
        return int(principal * (1 + (rate / n)) ** (n * time))
    else:
        principal, rate, n =  inv_amount or 0, percent/100,RD_options[freq]
        rate_div=rate/n
        total_frequency=get_duration(inv_date,mat_date,freq)
        return principal * (((1 + rate_div) ** total_frequency - 1) / rate_div) * (1 + rate_div)


def calculate_cumulative_interest_1(r,till_date):
    if r['maturity_date'].year!=2099:return r['maturity_value']
    till_date=min(datetime.combine(till_date, datetime.min.time()) ,r['maturity_date'])
    if r['type']=='FD':
        principal, rate, time, n =  r['investment_value'], r['percent_return']/100, till_date.year - r['invest_date'].year,1
        return int(principal * (1 + (rate / n)) ** (n * time))
    else:
        principal, rate, n =  r['investment_value'], r['percent_return']/100 ,RD_options[r['freq']]
        rate_div=rate/n
        total_frequency=get_duration(r['invest_date'],till_date,r['freq'])

        return principal * (((1 + rate_div) ** total_frequency - 1) / rate_div) * (1 + rate_div)

@st.cache_data
def get_firebase_data():
    data=[]
    for doc in collection.where(filter=FieldFilter("Close", "==", False)).stream():
        doc_dict=doc.to_dict()
        doc_dict['id']=doc.id
        data.append(doc_dict)
    data=pd.DataFrame.from_records(data)
    data['invest_date']=data['invest_date'].dt.tz_localize(None)
    data['maturity_date']=data['maturity_date'].dt.tz_localize(None)
    return data[['Select','investment_name','invest_date', 'maturity_date','investment_value','maturity_value', 'person', 'Edit','Close','investment_id', 'docs', 'type'
       , 'percent_return', 'freq','notes','id']]

@st.cache_data
def filter_investments(tgl_button, year,month, srch_txt,filter_person):
    filtered_df=get_firebase_data().copy(deep=True)
    
    if tgl_button:
        date_col="maturity_date"
        if year and month:
            end_date=date(year,month,30)
        elif year:
            end_date=date(year,12,31)
        else:
            end_date=date.today()

    else:
        date_col="invest_date"
        end_date=date.today()

    
    filtered_df['maturity_value'] = filtered_df.apply(lambda r:calculate_cumulative_interest_1(r,end_date), axis=1)                                     

    if not (year and month) or date_col=="maturity_date":
        filtered_df['investment_value'] =np.where(filtered_df['type'] == "RD", filtered_df.apply(lambda r:curr_invest_value(r,end_date),axis=1),filtered_df['investment_value'])

    if srch_txt:
        filtered_df = filtered_df[filtered_df['investment_name'].str.lower().str.contains(srch_txt)]
    if filter_person!="All":
        filtered_df = filtered_df[filtered_df['person']==filter_person]
    if date_col=="maturity_date":
        common_data=filtered_df[filtered_df[date_col].dt.year==2099].copy(deep=True)

    if year:
        filtered_df = filtered_df[filtered_df[date_col].dt.year == year]
    if month:
        filtered_df = filtered_df[filtered_df[date_col].dt.month == months.index(month)]
    if date_col=="maturity_date":
        return pd.concat([filtered_df,common_data])
    return filtered_df


def get_duration(start_date, end_date, unit):
    if unit == 'Yearly':
        return end_date.year - start_date.year
    elif unit == 'Monthly':
        years_diff = end_date.year - start_date.year
        months_diff = end_date.month - start_date.month
        return years_diff * 12 + months_diff
    elif unit == 'Weekly':
        total_days = (end_date - start_date).days
        return total_days // 7  # Integer division to get whole weeks
    elif unit == 'Daily':
        return (end_date - start_date).days
    
collection, bucket = firestore.client().collection("investments"), storage.bucket()
