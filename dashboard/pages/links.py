import streamlit as st


def links_index():
    st.header('한국투자증권 API')
    
    st.link_button('한국투자증권 API', 'https://apiportal.koreainvestment.com/intro')
    st.link_button('API 문서', 'https://apiportal.koreainvestment.com/apiservice-summary')
    st.link_button('종목정보 파일', 'https://apiportal.koreainvestment.com/apiservice-category')
    