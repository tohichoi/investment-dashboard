import streamlit as st


def settings_index():
    
    with st.form('settings_form'):
        st.number_input('검색 주기')