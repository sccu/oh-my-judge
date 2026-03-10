import subprocess
import time
import os

def launch_chrome_with_debugging():
    """
    원격 디버깅 포트를 활성화한 상태로 크롬(또는 크로미움)을 실행합니다.
    """
    # Darwin(macOS)에서의 일반적인 크롬/크로미움 경로
    chrome_paths = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "/usr/local/bin/chrome"
    ]
    
    chrome_path = next((path for path in chrome_paths if os.path.exists(path)), None)
    
    if not chrome_path:
        print("Chrome binary not found. Please ensure Google Chrome is installed.")
        return None

    print(f"Launching Chrome from: {chrome_path}")
    
    # 원격 디버깅 포트 9222 활성화
    # --remote-debugging-port: CDP 접속 허용
    # --user-data-dir: 별도의 프로필 디렉토리 사용 (기존 세션과 분리)
    # --headless=new: 최신 헤드리스 모드 (필요시 제거 가능)
    user_data_dir = os.path.abspath("tests/stealth/chrome_profile")
    os.makedirs(user_data_dir, exist_ok=True)
    
    cmd = [
        chrome_path,
        "--remote-debugging-port=9222",
        f"--user-data-dir={user_data_dir}",
        "--no-first-run",
        "--no-default-browser-check"
        # "--headless=new" (헤드리스 모드 해제)
    ]
    
    # 백그라운드 프로세스로 실행
    process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("Chrome launched with remote-debugging-port=9222")
    
    # 브라우저가 완전히 뜰 때까지 충분히 대기 (5초 이상)
    time.sleep(7)
    
    # 실행 중인지 확인
    if process.poll() is None:
        print(f"Chrome is running (PID: {process.pid})")
    else:
        print(f"Chrome failed to start or exited immediately (Exit code: {process.returncode})")
        
    return process

if __name__ == "__main__":
    launch_chrome_with_debugging()
