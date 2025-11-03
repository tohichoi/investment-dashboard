from datetime import datetime
import threading
import time
import streamlit as st
import schedule
from downloader.kis import download_all_kis_data


st.set_page_config(layout="wide")


def index():
    pg = st.navigation(["pages/investment_principles.py", "pages/overview.py", "pages/liquidity.py", "pages/google_trends.py", "pages/settings.py"])
    pg.run()


# 1. 주기적으로 실행할 작업 함수 정의
def scheduled_kis_job():
    """백그라운드에서 실행될 작업. Streamlit UI와 독립적입니다."""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Streamlit의 session_state에 직접 접근하려면 추가적인 고려가 필요하지만,
    # 여기서는 독립적인 작업을 수행한다고 가정합니다.
    print(f"✅ 백그라운드 작업 실행: {current_time}")
    
    download_all_kis_data()
    

# 2. schedule.run_pending()을 반복적으로 실행할 함수
def run_schedule():
    """스케줄링된 작업의 pending 상태를 확인하고 실행하는 무한 루프."""
    while True:
        schedule.run_pending()
        time.sleep(60) # 60초마다 대기
        
        
# 3. Streamlit 앱 실행 전 스케줄러 스레드 시작
def start_scheduler_thread():
    """스케줄러를 별도의 데몬 스레드로 시작합니다."""
    schedule.every().day.at("07:30", "Asia/Seoul").do(scheduled_kis_job)

    # 스케줄러 루프를 실행할 스레드를 생성하고 시작합니다.
    schedule_thread = threading.Thread(target=run_schedule, daemon=True)
    schedule_thread.start()
    
    st.info("스케줄러 백그라운드 스레드가 시작되었습니다.")
    return schedule_thread


if __name__ == "__main__":
    if 'scheduler_started' not in st.session_state:
        start_scheduler_thread()
        st.session_state.scheduler_started = True

    index()

