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
import json

# 用來停止腳本的標誌
stop_script = False
start_script = False

star_match_count = 3  # 預設值
target_match_count = 1  # 預設值
save_star_screenshot = True  # 預設值
save_target_screenshot = False  # 預設值

def get_screen_width():
    """獲取螢幕寬度解析度"""
    user32 = ctypes.windll.user32
    screen_width = user32.GetSystemMetrics(0)  # 螢幕寬度
    print(f"螢幕解析度寬度：{screen_width}")
    return screen_width

def get_btn_folder():
    """根據解析度選擇正確的資料夾"""
    screen_width = get_screen_width()
    folder = (f"btns/{screen_width}")
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
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            print(f"已從config.json載入設定")
            return config
    except FileNotFoundError:
        print("找不到config.json檔案，將使用預設值")
        return {"target_count": 1}  # 預設值
    except json.JSONDecodeError:
        print("config.json格式錯誤，將使用預設值")
        return {"target_count": 1}  # 預設值

def load_image(image_path):
    absolute_path = resource_path(image_path)
    image = cv2.imread(absolute_path, cv2.IMREAD_COLOR)
    if image is None:
        print(f"錯誤：無法載入圖片 {image_path}")
    else:
        print(f"已載入圖片：{image_path}")
    return image

def template_matching(screenshot, template, threshold=0.8, min_distance=20):
    screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    result = cv2.matchTemplate(screenshot_gray, template_gray, cv2.TM_CCOEFF_NORMED)
    loc = np.where(result >= threshold)

    points = []
    for pt in zip(*loc[::-1]):
        points.append([pt[0], pt[1], template.shape[1], template.shape[0]])

    rects, _ = cv2.groupRectangles(points, groupThreshold=1, eps=0.5)
    final_points = [(int(x + w / 2), int(y + h / 2)) for x, y, w, h in rects]

    return final_points

def btn_matching(screenshot, template):
    screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    w, h = template_gray.shape[::-1]

    result = cv2.matchTemplate(
        screenshot_gray, template_gray, cv2.TM_CCOEFF_NORMED)
    threshold = 0.6
    loc = np.where(result >= threshold)

    points = []
    for pt in zip(*loc[::-1]):
        points.append((pt[0] + w // 2, pt[1] + h // 2))

    return points

def capture_screenshot():
    screenshot = pyautogui.screenshot()
    screenshot = np.array(screenshot)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
    return screenshot

def check_star_count(screenshot, template):
    star_count = 0
    points = template_matching(screenshot, template)
    if points:
        star_count = len(points)
        if star_count >= star_match_count:
            print(f"已找到 {star_count} 個5星角色，已滿足條件({star_match_count}以上)")
            if save_target_screenshot:
                save_screenshot()
            return True
    return False

def check_templates(screenshot, templates):
    match_count = 0
    for template in templates:
        points = template_matching(screenshot, template)
        if points:
            count = len(points)
            match_count += count
            print(f"找到角色圖片，共找到 {count} 個角色匹配點")
        if match_count >= target_match_count:
            print(f"已找到至少 {target_match_count} 張角色圖片")
            if save_star_screenshot:
                save_screenshot()
            return True
    if match_count == 0:
        print("未找到任何匹配角色圖片")
    return False

def save_screenshot():
    # 擷取目前螢幕畫面
    img = take_screenshot()
    img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    # 確保 screenshots 資料夾存在
    screenshots_dir = os.path.join(os.getcwd(), "screenshots")
    os.makedirs(screenshots_dir, exist_ok=True)

    # 使用時間戳命名並儲存截圖
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(screenshots_dir, f"screenshot_{timestamp}.png")
    cv2.imwrite(filename, img)
    print(f"已截圖，已存放在目錄: {filename}")


def process_buttons_and_templates(iteration, retry_template, retry_confirm_template, skip_template, star_template, templates):
    global stop_script

    screenshot = capture_screenshot()

    retry_points = btn_matching(screenshot, retry_template)
    if not retry_points:
        print("未找到Retry按鈕")
        return False

    pyautogui.click(retry_points[0])
    print("已點擊retry按鈕")
    time.sleep(1)  # 根據電腦效能修改,建議為 1~2秒

    screenshot = capture_screenshot()
    retry_confirm_points = btn_matching(screenshot, retry_confirm_template)
    if not retry_confirm_points:
        print("未找到Retry confirm按鈕")
        return False

    pyautogui.click(retry_confirm_points[0])
    print("已點擊retry confirm按鈕")
    time.sleep(1)  # 根據電腦效能修改,建議為 1~2秒

    screenshot = capture_screenshot()
    skip_points = btn_matching(screenshot, skip_template)
    if not skip_points:
        print("未找到Skip按鈕")
        return False

    pyautogui.click(skip_points[0])
    print("已點擊skip按鈕")
    time.sleep(1)  # 根據電腦效能修改,建議為 1~2秒

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
        save_target_screenshot = config.get('save_target_screenshot', False)

        print(f"""
設定資訊：
- 5 星數量目標: {config.get('star_count', 3)}
- 目標匹配數量: {target_match_count}
- 5星數量達標時截圖: {config.get('save_target_screenshot', False)}
- 目標匹配達標時截圖: {config.get('save_star_screenshot', True)}
""")

        template_count = get_template_count()
        if template_count == 0:
            print("未找到任何範例圖片，無法執行。")
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
                found = process_buttons_and_templates(
                    iteration, retry_template, retry_confirm_template, skip_template, star_template, templates)
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
