from datetime import datetime
import threading
import time
import streamlit as st
import schedule
from downloader.kis import download_all_kis_data


st.set_page_config(layout="wide")


def index():
    pg = st.navigation(["pages/overview.py", "pages/liquidity.py", "pages/google_trends.py", "pages/settings.py"])
    pg.run()


# 1. 주기적으로 실행할 작업 함수 정의
def scheduled_job():
    """백그라운드에서 실행될 작업. Streamlit UI와 독립적입니다."""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Streamlit의 session_state에 직접 접근하려면 추가적인 고려가 필요하지만,
    # 여기서는 독립적인 작업을 수행한다고 가정합니다.
    print(f"✅ 백그라운드 작업 실행: {current_time}")
    
    download_all_kis_data()
    
    # 예시로, Streamlit의 session_state에 접근하지 않고 독립적인 작업을 수행합니다.
    # st.session_state를 스레드에서 업데이트하려면 Streamlit의 특정 컨텍스트 처리가 필요합니다.
    if 'job_log' not in st.session_state:
        st.session_state.job_log = []
    
    # 메인 스레드가 아닌 다른 스레드에서 st.session_state를 업데이트하면 오류가 발생할 수 있습니다.
    # 간단한 예시를 위해 print만 사용하거나, 안전한 방식으로 데이터를 공유해야 합니다.
    # st.session_state.job_log.append(f"작업 완료: {current_time}")
    

# 2. schedule.run_pending()을 반복적으로 실행할 함수
def run_schedule():
    """스케줄링된 작업의 pending 상태를 확인하고 실행하는 무한 루프."""
    while True:
        schedule.run_pending()
        time.sleep(1) # 1초마다 대기
        
        
# 3. Streamlit 앱 실행 전 스케줄러 스레드 시작
def start_scheduler_thread():
    """스케줄러를 별도의 데몬 스레드로 시작합니다."""
    schedule.every().day.at("07:30", "Asia/Seoul").do(scheduled_job)

    # 스케줄러 루프를 실행할 스레드를 생성하고 시작합니다.
    schedule_thread = threading.Thread(target=run_schedule, daemon=True)
    schedule_thread.start()
    
    st.write("스케줄러 백그라운드 스레드가 시작되었습니다.")
    return schedule_thread


if __name__ == "__main__":
    if 'scheduler_started' not in st.session_state:
        start_scheduler_thread()
        st.session_state.scheduler_started = True

    index()

