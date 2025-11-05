from datetime import datetime
from pathlib import Path
import threading
import time
import schedule
from downloader.kis import download_all_kis_data
from rich import print


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
    schedule.every().hour.do(scheduled_kis_job)

    # 스케줄러 루프를 실행할 스레드를 생성하고 시작합니다.
    schedule_thread = threading.Thread(target=run_schedule, daemon=True)
    schedule_thread.start()
    
    return schedule_thread


def wait_for_thread_terminated(thread):
    schedule_thread.join(None)
    while schedule_thread.is_alive():
        print('Waiting for thread being terminated ...')
        time.sleep(1)    


if __name__ == "__main__":
    try:
        print('Starting scheduler')
        schedule_thread = start_scheduler_thread()
        wait_for_thread_terminated(schedule_thread)
    except KeyboardInterrupt:
        pass
    finally:
        wait_for_thread_terminated(schedule_thread)
        
    print("스크립트 실행 완료 및 종료.")