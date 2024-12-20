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
    """判斷螢幕截圖上是有與範例圖片匹配的點
    Args:
        screenshot (np.array): 螢幕截圖的numpy陣列
        template (np.array): 範例圖片
        threshold (float): 匹配閾值
        use_rect (bool): 是否使用矩形框(按鈕情況不使用)
    Returns:
        np.array: 匹配點的座標
    """
    screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    result = cv2.matchTemplate(screenshot_gray, template_gray, cv2.TM_CCOEFF_NORMED)
    loc = np.where(result >= threshold)

    points = []
    if use_rect:
        for pt in zip(*loc[::-1]):
            points.append([pt[0], pt[1], template.shape[1], template.shape[0]])
        rects, _ = cv2.groupRectangles(points, groupThreshold=1, eps=0.5)
        final_points = [(int(x + w / 2), int(y + h / 2)) for x, y, w, h in rects]
    else:
        final_points = [(int(x), int(y)) for x, y in zip(*loc[::-1])]

    return final_points

def star_matching(screenshot, template):
    """5星抓點"""
    global width
    if width > 1920:
        threshold = 0.8
    else:
        threshold = 0.78
    points = template_matching(screenshot, template, threshold, True)
    return points

def btn_matching(screenshot, template):
    """按鈕抓點"""
    points = template_matching(screenshot, template, 0.6, False)
    return points

def check_star_count(screenshot, template):
    """判斷是否滿足5星數量條件"""
    if star_match_count == 0:
        print("5星數量目標為 0，已滿足條件")
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
    return False

def check_templates(screenshot, templates):
    """判斷是否滿足目標匹配條件"""
    if target_match_count == 0:
        print("目標匹配數量為 0，已滿足條件")
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

def save_screenshot():
    capture_screenshot(save_to_file=True)

def click_btns(retry_template, retry_confirm_template, skip_template):
    """點擊按鈕循環"""
    for btn, desc in [(retry_template, "Retry"), (retry_confirm_template, "Retry Confirm"), (skip_template, "Skip")]:
        screenshot = capture_screenshot()
        points = btn_matching(screenshot, btn)
        if points:
            pyautogui.click(points[0])
            print(f"已點擊 {desc}")
            time.sleep(delay_time) # 根據電腦效能修改,建議為 1~2秒
        else:
            print(f"未找到 {desc} 按鈕")
            return False
        
    check_else_skip(retry_template, retry_confirm_template, skip_template)
        
    
def check_else_skip(retry_template, retry_confirm_template, skip_template):
    """判斷當前畫面是否還有額外的Skip按鈕，有的話點擊該按鈕，並進入新的按鈕循環"""
    screenshot = capture_screenshot()
    points = btn_matching(screenshot, skip_template)
    if points:
        pyautogui.click(points[0])
        print("已點擊Skip按鈕")
        time.sleep(delay_time) # 根據電腦效能修改,建議為 1~2秒

        click_btns(retry_template, retry_confirm_template, skip_template) #進新的循環

    else:
        print("當前畫面已無額外的Skip按鈕，開始執行匹配判斷...")

def process_buttons_and_templates(iteration, retry_template, retry_confirm_template, skip_template, star_template, templates):
    """處理按鈕點擊和範例圖片匹配判斷"""
    global stop_script
    global delay_time

    click_btns(retry_template, retry_confirm_template, skip_template)

    screenshot = capture_screenshot()
    # 判斷是否滿足星數條件
    if check_star_count(screenshot, star_template):
        # 判斷是否滿足目標匹配條件
        if check_templates(screenshot, templates):
            print("已滿足所有條件。退出...")
            return True
    return False

def toggle_start_stop():
    """按下F9鍵啟動或停止腳本"""
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
    """獲取範例圖片資料夾內圖片數量"""
    templates_dir = os.path.join(os.getcwd(), "templates")
    if not os.path.exists(templates_dir):
        print("templates 資料夾不存在！請確認路徑。")
        return 0

    files = [f for f in os.listdir(templates_dir) if os.path.isfile(os.path.join(templates_dir, f))]
    return len(files)

def rewrite_log(iteration, found):
    """重寫log，每次清空舊內容只保留最新結果"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # 使用 'w' 模式會自動創建不存在的檔案，並清空既有內容
    with open("log.txt", "w") as file:
        file.write(f"運行次數: {iteration}\n是否滿足條件: {found}\n最後執行時間: {timestamp}")

def main():
    """主函數"""
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
            print("未找到任何範例圖片，已強制將目標匹配數量設定為 0")
            target_match_count = 0
        else:
            print(f"範例資料夾內有: {template_count} 張範例圖片。")

        folder = get_btn_folder()
        retry_template = load_image(f'{folder}/retry.png')
        retry_confirm_template = load_image(f'{folder}/retry_confirm.png')
        skip_template = load_image(f'{folder}/skip.png')
        star_template = load_image(f'{folder}/5star.png')
        templates = [load_image(f'templates/t{i + 1}.png') for i in range(template_count)]
        print("範例圖片載入完成，請於遊戲抽卡畫面按下 F9 開始運行腳本")

        while True:
            while not start_script:
                time.sleep(0.1)

            iteration = 0 # 運行次數
            stop_script = False # 停止腳本標誌

            while start_script:
                iteration += 1
                print(f"運行次數 {iteration}")
                found = process_buttons_and_templates(iteration, retry_template, retry_confirm_template, skip_template, star_template, templates)
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
