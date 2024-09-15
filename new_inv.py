from datetime import date, datetime
import random
import string
import streamlit_antd_components as sac
import streamlit as st
from streamlit_free_text_select import st_free_text_select
from dateutil.relativedelta import relativedelta
from utils import *

def upload_to_firebase():
    inv_docs=[]
    for file_obj in st.session_state['files_ip']:
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
        "investment_id":st.session_state["inv_id_ip"],
        "investment_name":st.session_state["inv_name_ip"],
        "type":st.session_state["type_ip"],
        "person":st.session_state["person_ip"],
        "investment_value": st.session_state['inv_amount_ip'],
        "maturity_value":st.session_state['mat_amount_ip'],
        "invest_date":datetime.combine(st.session_state['inv_date_ip'] , datetime.min.time()),
        "matrurity_date":datetime.combine(st.session_state['inv_date_ip'] , datetime.min.time()),
        "percent_return": st.session_state['percent_ip'],
        "notes":st.session_state["notes_ip"],
        "docs":inv_docs,
        "closed":False
    })
        
def change_maturity_date():
    if st.session_state['yrs_ip']!="Inf":
        st.session_state['mat_date_ip']=st.session_state['inv_date_ip'] + relativedelta(years=st.session_state['yrs_ip'])
    else:
        st.session_state['mat_date_ip']=date(2099,1,1)

def calculate_cumulative_interest_helper():
    st.session_state['mat_amount_ip']=calculate_cumulative_interest(
        st.session_state['inv_amount_ip'],
        st.session_state['percent_ip'],
        st.session_state['mat_date_ip'],
        st.session_state['inv_date_ip'],
        st.session_state['freq_ip'],
        st.session_state['type_ip'])
    
@st.dialog("Add / Edit Investment")
def add_inv(inv_names,type_idx,person_idx,edit=False):
    
    sac.segmented(
    key="type_ip",
    index=type_idx,
    items=[
            sac.SegmentedItem(label=x) for x in types_data
        ], label='', align='center')

    sac.segmented(
    key="person_ip",
    index=person_idx,
    items=[
            sac.SegmentedItem(label=x) for x in people
        ]
    , label='', align='center'
    )
    st.text_input(label="Investment ID",placeholder="Enter Investment ID",key="inv_id_ip")
    st_free_text_select(
            options=inv_names,
            label="Investment Name",
            key="inv_name_ip",
            index=inv_names.index(st.session_state['inv_name_ip']) if st.session_state['inv_name_ip'] in inv_names else None,
            placeholder="Select an Investment or Enter new name",
            disabled=False,
            delay=300,
            label_visibility="visible",
        )
    st.date_input(label="Investment Date",key="inv_date_ip")
    if st.session_state["type_ip"]=="FD":
        col7,col8 = st.columns([1,1],vertical_alignment="bottom")
        with col7:
            st.date_input(label="Maturity Date",key="mat_date_ip")
        with col8:
            st.selectbox(label="Yrs",options=yrs_options,on_change=change_maturity_date,key="yrs_ip")
    else:
        col7,col8,col_rd = st.columns([1,1,1],vertical_alignment="bottom")
        with col7:
            st.date_input(label="Maturity Date",key="mat_date_ip")
        with col8:
            st.selectbox(label="Yrs",options=yrs_options,on_change=change_maturity_date,key="yrs_ip",index=yrs_options.index(st.session_state['yrs_ip']))
        with col_rd:
            st.selectbox(label="Frequency",options=RD_options_list,key="freq_ip",index=RD_options_list.index(st.session_state['freq_ip']))



    st.number_input("Investment Amount",key="inv_amount_ip",step=500)
    col9,col10,col11 = st.columns([1,2,1],vertical_alignment="bottom")

    if "percent_ip" not in st.session_state:
            st.session_state["percent_ip"] = 8

    col9.number_input("Percent",step=1,key="percent_ip")
    col10.number_input("Maturity Amount",step=500,key="mat_amount_ip")
    col11.button("CP interest",on_click=calculate_cumulative_interest_helper)

    st.text_area("Additional notes",key="notes_ip")

    st.file_uploader(
        "Upload investment proofs",type=["pdf","jpeg","png","jpg"] ,accept_multiple_files=True,
        key="files_ip",

    )
    _, coly, _ = st.columns([5,3,5])

    coly.button('Submit' if not edit else 'Update',on_click=upload_to_firebase)


