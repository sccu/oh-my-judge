import time
import random
import math

class HumanoidInteractor:
    """
    Playwright Page 객체를 래핑하여 사람과 유사한 인터랙션을 수행합니다.
    """
    def __init__(self, page):
        self.page = page

    def type_humanly(self, selector, text, delay_range=(0.05, 0.25)):
        """
        글자마다 랜덤한 지연 시간을 두어 타이핑합니다.
        가끔 오타를 냈다가 지우는 행동을 모사할 수도 있습니다.
        """
        self.page.click(selector)
        for char in text:
            self.page.keyboard.type(char)
            time.sleep(random.uniform(*delay_range))
        print(f"[Humanoid] Typed '{text}' into {selector}")

    def move_mouse_humanly(self, target_x, target_y, steps=10):
        """
        단순 직선이 아닌, 중간 점들을 거쳐 마우스를 이동합니다.
        (향후 Bezier 곡선으로 더 정교하게 발전시킬 수 있습니다.)
        """
        start_x, start_y = self.page.mouse._impl._last_move_id if hasattr(self.page.mouse, '_impl') else (0, 0)
        # 실제로는 page.evaluate로 현재 마우스 위치를 알기 어려우므로 상대적 이동이나 목표점 기반으로 수행
        
        for i in range(1, steps + 1):
            # 목표 지점 주변으로 미세하게 흔들림 추가
            jitter_x = random.uniform(-2, 2)
            jitter_y = random.uniform(-2, 2)
            
            # 선형 보간에 지터 추가
            current_x = start_x + (target_x - start_x) * (i / steps) + jitter_x
            current_y = start_y + (target_y - start_y) * (i / steps) + jitter_y
            
            self.page.mouse.move(current_x, current_y)
            time.sleep(random.uniform(0.01, 0.03))

    def click_humanly(self, selector):
        """
        요소의 중심이 아닌 무작위 지점을 클릭합니다.
        """
        box = self.page.locator(selector).bounding_box()
        if box:
            # 버튼 영역 내에서 랜덤한 좌표 선택
            target_x = box['x'] + box['width'] * random.uniform(0.2, 0.8)
            target_y = box['y'] + box['height'] * random.uniform(0.2, 0.8)
            
            self.move_mouse_humanly(target_x, target_y)
            time.sleep(random.uniform(0.1, 0.3))
            self.page.mouse.click(target_x, target_y)
            print(f"[Humanoid] Clicked {selector} at ({target_x:.1f}, {target_y:.1f})")

    def wait_randomly(self, min_sec=1, max_sec=3):
        """
        사람이 화면을 보는 듯한 자연스러운 대기를 수행합니다.
        """
        duration = random.uniform(min_sec, max_sec)
        time.sleep(duration)
