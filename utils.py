import os
from firebase_admin import firestore,storage
import streamlit as st
from streamlit_google_auth_handler import Authenticate
from consts import *

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
