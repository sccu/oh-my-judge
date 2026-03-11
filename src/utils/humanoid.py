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

    def move_mouse_humanly(self, target_x, target_y, steps=25):
        """
        Bezier 곡선을 활용하여 가속/감속이 포함된 비선형 궤적을 생성하고 마우스를 이동합니다.
        """
        # 현재 마우스 위치 (Playwright에서는 직접 가져오기 어려우므로 0,0 또는 마지막 위치 가정)
        # 실제로는 상태 추적이 필요하지만, 여기선 간단히 직선에 곡률을 더함
        start_x, start_y = (random.randint(0, 100), random.randint(0, 100))
        
        # 제어점(Control Point) 생성 (곡선을 위해)
        control_x = (start_x + target_x) / 2 + random.uniform(-100, 100)
        control_y = (start_y + target_y) / 2 + random.uniform(-100, 100)

        def get_bezier_point(t, p0, p1, p2):
            return (1 - t)**2 * p0 + 2 * (1 - t) * t * p1 + t**2 * p2

        for i in range(1, steps + 1):
            t = i / steps
            # Quadratic Bezier
            current_x = get_bezier_point(t, start_x, control_x, target_x)
            current_y = get_bezier_point(t, start_y, control_y, target_y)
            
            # 미세 지터(Jitter) 추가
            current_x += random.uniform(-1, 1)
            current_y += random.uniform(-1, 1)
            
            self.page.mouse.move(current_x, current_y)
            
            # 가속/감속 모사 (중간이 빠르고 끝이 느림)
            wait_time = 0.005 + (math.sin(t * math.pi) * 0.01)
            time.sleep(wait_time)

        print(f"[Humanoid] Moved mouse to ({target_x:.1f}, {target_y:.1f}) via Bezier curve")

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
