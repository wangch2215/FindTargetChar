import cv2
import numpy as np
import pyautogui
import time
import keyboard
import threading
from PIL import Image
import sys
import os
from datetime import datetime
from pyautogui import screenshot as take_screenshot
import ctypes

# 用來停止腳本的標誌
stop_script = False
start_script = False

star_match_count = 3  # 預設值
target_match_count = 1  # 預設值
save_star_screenshot = True  # 預設值
save_target_screenshot = False  # 預設值
delay_time = 1.0 # 預設值

width = 3840

def get_screen_width():
    """獲取螢幕寬度解析度"""
    user32 = ctypes.windll.user32
    screen_width = user32.GetSystemMetrics(0)  # 螢幕寬度
    print(f"螢幕解析度寬度：{screen_width}")
    return screen_width

def get_btn_folder():
    global width
    """根據解析度選擇正確的資料夾"""
    width = get_screen_width()
    folder = (f"btns/{width}")
    print(f"選擇的資料夾：{folder}")
    return folder

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def load_config():
    try:
        import configparser
        config = configparser.ConfigParser()
        config.read('config.ini', encoding='utf-8')
        
        return {
            "star_count": config.getint('Settings', 'star_count', fallback=3),
            "target_count": config.getint('Settings', 'target_count', fallback=1),
            "save_star_screenshot": config.getboolean('Settings', 'save_star_screenshot', fallback=True),
            "save_target_screenshot": config.getboolean('Settings', 'save_target_screenshot', fallback=True),
            "delay_time": config.getfloat('Settings', 'delay_time', fallback=1.0)
        }
    except Exception as e:
        print(f"讀取設定檔時發生錯誤：{e}，將使用預設值")
        return {
            "star_count": 3,
            "target_count": 1,
            "save_star_screenshot": True,
            "save_target_screenshot": True,
            "delay_time": 1.0
        }

def load_image(image_path):
    absolute_path = resource_path(image_path)
    image = cv2.imread(absolute_path, cv2.IMREAD_COLOR)
    if image is None:
        print(f"錯誤：無法載入圖片 {image_path}")
    else:
        print(f"已載入圖片：{image_path}")
    return image

def template_matching(screenshot, template, threshold=0.8, use_rect=True):
    """
    統一的模板匹配函式

    參數:
        screenshot: 螢幕截圖影像 (BGR 格式)
        template: 模板影像 (BGR 格式)
        threshold: 匹配的門檻值
        use_rect: 是否合併重疊區域 (True 使用 groupRectangles, False 直接回傳匹配點)

    回傳:
        final_points: 匹配點的中心座標列表
    """

    screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    result = cv2.matchTemplate(screenshot_gray, template_gray, cv2.TM_CCOEFF_NORMED)
    loc = np.where(result >= threshold)

    w, h = template_gray.shape[::-1]

    points = []
    if use_rect:
        for pt in zip(*loc[::-1]):
            points.append([pt[0], pt[1], w, h])

        rects, _ = cv2.groupRectangles(points, groupThreshold=1, eps=0.5)
        final_points = [(int(x + w / 2), int(y + h / 2)) for x, y, w, h in rects]

        return final_points
    else:
        for pt in zip(*loc[::-1]):
            points.append((pt[0] + w // 2, pt[1] + h // 2))
        return points
    
def star_matching(screenshot, template):
    """5星角色匹配
    Args:
        screenshot: 螢幕截圖影像 (BGR 格式)
        template: 5星角色範例圖片
    Returns:
        list: 匹配點的中心座標列表
    """
    global width
    if width > 1920:
        threshold = 0.8
    else:
        threshold = 0.78
    return template_matching(screenshot, template, threshold, True)

def btn_matching(screenshot, template):
    """按鈕匹配
    Args:
        screenshot: 螢幕截圖影像 (BGR 格式)
        template: 按鈕範例圖片
    Returns:
        list: 匹配點的中心座標列表
    """
    return template_matching(screenshot, template, 0.6, False)

def check_star_count(screenshot, template):
    """檢查是否找到足夠的5星角色
    Args:
        screenshot: 螢幕截圖影像 (BGR 格式)
        template: 5星角色範例圖片
    Returns:
        bool: 是否找到足夠的角色圖片
    """
    if star_match_count == 0:
        print(f"未設置5星數量目標，直接進行目標匹配")
        if save_star_screenshot:
            save_screenshot()
        return True
    
    star_count = 0
    points = star_matching(screenshot, template)
    if points:
        star_count = len(points)
        if star_count >= star_match_count:
            print(f"已找到 {star_count} 個5星角色，已滿足條件({star_match_count}以上)")
            if save_star_screenshot:
                save_screenshot()
            return True
        else:
            print(f"未找到足夠的5星角色，目前找到 {star_count} 個")
            return False
    else:
        print("未找到任何5星角色")
        return False

def check_templates(screenshot, templates):
    """檢查是否找到足夠的角色圖片
    Args:
        screenshot: 螢幕截圖影像 (BGR 格式)
        templates: 角色圖片列表
    Returns:
        bool: 是否找到足夠的角色圖片
    """
    if target_match_count == 0:
        print(f"未設置目標匹配數量，已滿足條件")
        if save_target_screenshot:
            save_screenshot()
        return True
    
    match_count = 0
    for template in templates:
        points = template_matching(screenshot, template)
        if points:
            count = len(points)
            match_count += count
            print(f"找到角色圖片，共找到 {count} 個角色匹配點")
        if match_count >= target_match_count:
            print(f"已找到至少 {target_match_count} 張角色圖片")
            if save_target_screenshot:
                save_screenshot()
            return True
    if match_count == 0:
        print("未找到任何匹配角色圖片")
    return False

def capture_screenshot(save_to_file=False):
    """擷取螢幕畫面，可選擇是否儲存檔案
    Args:
        save_to_file (bool): 是否儲存為檔案
    Returns:
        np.array: 螢幕截圖的numpy陣列
    """
    screenshot = pyautogui.screenshot()
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    
    if save_to_file:
        # 確保 screenshots 資料夾存在
        screenshots_dir = os.path.join(os.getcwd(), "screenshots")
        os.makedirs(screenshots_dir, exist_ok=True)

        # 使用時間戳命名並儲存截圖
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(screenshots_dir, f"screenshot_{timestamp}.png")
        cv2.imwrite(filename, screenshot)
        print(f"已截圖，已存放在目錄: {filename}")
    
    return screenshot

# 為了向後相容，可以保留save_screenshot函數
def save_screenshot():
    capture_screenshot(save_to_file=True)


def click_buttons( retry_template, retry_confirm_template, skip_template):
    """點擊按鈕操作
    Args:
        retry_template: 重試按鈕範例圖片
        retry_confirm_template: 重試確認按鈕範例圖片
        skip_template: 跳過按鈕範例圖片
    Returns:
        bool: 是否成功點擊按鈕
    """
    global delay_time
    for btn, btn_name in [(retry_template, "retry"), (retry_confirm_template, "retry_confirm"), (skip_template, "skip")]:
        screenshot = capture_screenshot()
        points = btn_matching(screenshot, btn)
        if not points:
            print(f"未找到{btn_name}按鈕")
            return False
        pyautogui.click(points[0])
        print(f"已點擊{btn_name}按鈕")
        time.sleep(delay_time)  # 根據電腦效能修改,建議為 1~2秒

def process_buttons_and_templates(retry_template, retry_confirm_template, skip_template, star_template, templates):
    global stop_script
    global delay_time

    click_buttons(retry_template, retry_confirm_template, skip_template)

    screenshot = capture_screenshot()
    if check_star_count(screenshot, star_template):
        if check_templates(screenshot, templates):
            print("已滿足所有條件。退出...")
            return True
    return False

def toggle_start_stop():
    global stop_script, start_script
    while True:
        if keyboard.is_pressed('F9'):
            if start_script:
                print("按下F9鍵。停止腳本...")
                stop_script = True
                start_script = False
            else:
                print("按下F9鍵。啟動腳本...")
                stop_script = False
                start_script = True
            time.sleep(0.5)

def get_template_count():
    templates_dir = os.path.join(os.getcwd(), "templates")
    if not os.path.exists(templates_dir):
        print("templates 資料夾不存在！請確認路徑。")
        return 0

    files = [f for f in os.listdir(templates_dir) if os.path.isfile(os.path.join(templates_dir, f))]
    return len(files)

def rewrite_log(iteration, found):
    try:
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open('log.txt', 'w', encoding='utf-8') as f:
            f.write(f"運行次數: {iteration}\n是否符合條件: {found}\n紀錄時間: {date}\n")
    except Exception as e:
        print(f"寫入記錄檔時發生錯誤: {e}")
        print("繼續執行腳本...")

def main():
    global stop_script, start_script
    global star_match_count, target_match_count
    global save_star_screenshot, save_target_screenshot

    try:
        threading.Thread(target=toggle_start_stop, daemon=True).start()

        # 從config讀取target_count
        config = load_config()
        star_match_count = config.get('star_count', 3)
        target_match_count = config.get('target_count', 1)
        save_star_screenshot = config.get('save_star_screenshot', True)
        save_target_screenshot = config.get('save_target_screenshot', True)
        delay_time = config.get('delay_time', 1)

        print(f"""
設定資訊：
- 5 星數量目標: {star_match_count}
- 目標匹配數量: {target_match_count}
- 5星數量達標時截圖: {save_star_screenshot}
- 目標匹配達標時截圖: {save_target_screenshot}
- 延遲時間: {delay_time}
""")

        template_count = get_template_count()
        if template_count == 0:
            print("未找到任何範例圖片，強制將匹配數量設置為0")
            target_match_count = 0
        else:
            print(f"範例圖片數量自動設定為: {template_count}")

        btn_folder = get_btn_folder()

        retry_template = load_image(f'{btn_folder}/retry.png')
        retry_confirm_template = load_image(f'{btn_folder}/retry_confirm.png')
        skip_template = load_image(f'{btn_folder}/skip.png')

        star_template = load_image(f'{btn_folder}/5star.png')

        templates = [load_image(f'templates/t{i + 1}.png') for i in range(template_count)]
        print("範例圖片載入完成，請於遊戲抽卡畫面按下 F9 開始運行腳本")

        while True:
            while not start_script:
                time.sleep(0.1)

            iteration = 0
            stop_script = False

            while start_script:
                iteration += 1
                print(f"運行次數 {iteration}")
                found = process_buttons_and_templates(retry_template, retry_confirm_template, skip_template, star_template, templates)
                rewrite_log(iteration, found)
                if found or stop_script:
                    start_script = False
                    stop_script = True
                    break

                time.sleep(0.1)

            print("腳本已停止，等待重新啟動...")
    except Exception as e:
        print(f"運行過程中出現錯誤: {e}")
    finally:
        input("按下Enter鍵退出終端...")

if __name__ == "__main__":
    main()