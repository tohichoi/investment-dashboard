import streamlit as st
import streamlit.components.v1 as st_components


def load_dataset():
    st.markdown("## Google trends Analysis")
    st.markdown("#### 우리나라에서 KOSPI 관련 검색어 트렌드")
    google_trends_embed_code_kospi=r'''
        <script type="text/javascript" src="https://ssl.gstatic.com/trends_nrtr/4267_RC01/embed_loader.js"></script>
        <script type="text/javascript">
        trends.embed.renderExploreWidget("TIMESERIES", {"comparisonItem":[{"keyword":"kospi","geo":"KR","time":"today 3-m"}],"category":0,"property":""}, {"exploreQuery":"date=today%203-m&geo=KR&q=kospi&hl=en","guestPath":"https://trends.google.com:443/trends/embed/"});
        </script>
    '''
    st_components.html(google_trends_embed_code_kospi, height=500)
    
    st.markdown("#### Worldwide KOSPI+S&P500+NASDAQ 관련 검색어 트렌드")
    google_trends_embed_code_kospi_and_us_market=r'''
        <script type="text/javascript" src="https://ssl.gstatic.com/trends_nrtr/4267_RC01/embed_loader.js"></script>
        <script type="text/javascript">
        trends.embed.renderExploreWidget("TIMESERIES", {"comparisonItem":[{"keyword":"kospi","geo":"","time":"today 3-m"},{"keyword":"/m/016yss","geo":"","time":"today 3-m"},{"keyword":"nasdaq","geo":"","time":"today 3-m"}],"category":0,"property":""}, {"exploreQuery":"date=today%203-m&q=kospi,%2Fm%2F016yss,nasdaq&hl=en","guestPath":"https://trends.google.com:443/trends/embed/"});
        </script>
    '''
    st_components.html(google_trends_embed_code_kospi_and_us_market, height=500)

    st.markdown("#### 우리나라에서 주식, 부동산 관련 검색어 트렌드")
    google_trends_embed_code_real_estate_and_stock=r'''
        <script type="text/javascript" src="https://ssl.gstatic.com/trends_nrtr/4215_RC01/embed_loader.js"></script>
        <script type="text/javascript">
        trends.embed.renderExploreWidget("TIMESERIES", {"comparisonItem":[{"keyword":"부동산","geo":"KR","time":"today 3-m"},{"keyword":"주식","geo":"KR","time":"today 3-m"}],"category":0,"property":""}, {"exploreQuery":"date=today%203-m&geo=KR&q=%EB%B6%80%EB%8F%99%EC%82%B0,%EC%A3%BC%EC%8B%9D&hl=en","guestPath":"https://trends.google.com:443/trends/embed/"});
        </script>
    '''
    st_components.html(google_trends_embed_code_real_estate_and_stock, height=500)

def index():
    load_dataset()


index()