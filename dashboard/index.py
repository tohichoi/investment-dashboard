from datetime import datetime
import streamlit as st
from downloader.kis import download_all_kis_data


st.set_page_config(layout="wide")


def index():
    pg = st.navigation(["pages/investment_principles.py", "pages/short_term_view.py", 
                        "pages/long_term_view.py", "pages/liquidity.py", 
                        "pages/google_trends.py", "pages/settings.py"])
    pg.run()


if __name__ == "__main__":
    index()

