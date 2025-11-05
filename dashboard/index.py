import streamlit as st
from pages.short_term_view import short_term_view_index
from pages.long_term_view import long_term_view_index
from pages.google_trends import google_trends_index
from pages.settings import settings_index


st.set_page_config(layout="wide")


def index():
    pg = st.navigation([
                        short_term_view_index, 
                        long_term_view_index, 
                        google_trends_index, 
                        "pages/investment_principles.py", 
                        settings_index])
    pg.run()


if __name__ == "__main__":
    index()

