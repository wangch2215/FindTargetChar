# Auto-Clicker and Template Matching Script

這是一個用於自動點擊並匹配螢幕截圖中模板的腳本。此腳本會不斷捕捉螢幕截圖，尋找指定的按鈕並點擊它們，然後檢查截圖中是否存在指定的模板。
原代碼來自[Perry481/BD2-Script](https://github.com/Perry481/BD2-Script)，基於此原代碼做了一些修改。

## 功能

- 自動點擊指定按鈕（retry、retry confirm、skip）。
- 檢查螢幕截圖中是否存在指定模板。
- 檢查是否達到五星數量條件。
- 達到五星數量條件後，繼續檢查模板中是否存在指定的角色模板及數量。
- F9開始運行後，直到找到所需模板或按下F9鍵退出。

## 前置作業
- 調整螢幕解析度至 1920 * 1080 / 2560 * 1440 / 3840 * 2160
- 開啟遊戲，將遊戲以全螢幕模式運行
- 從resouces資料夾中挑選想要抽取的角色，複製圖片後貼到templates資料夾中，目前僅提供4K底下的部分 5 星截圖，其餘解析度麻煩自行製作範本圖片。
- 運行rename.py，會templates資料夾底下的檔案改名為t1.png、t2.png、t3.png...

## 注意事項
- 角色範本圖片請轉存為png格式。
- 角色範本圖片請使用英文+數字先隨意命名，中文命名可能會導致rename.py無法正常運作。

---

## 設定檔說明

在根目錄中的 `config.ini` 可以自訂腳本的運行設定：
(點擊右鍵以記事本開啟，即可編輯)

| 設定項目 | 說明 | 預設值 | 可選值 |
|---------|------|--------|--------|
| star_count | 需要的五星角色數量 | 3 | 任意正整數 |
| target_count | 需要匹配的目標角色數量 | 1 | 任意正整數 |
| save_star_screenshot | 當達到五星數量條件時是否截圖 | true | true/false |
| save_target_screenshot | 當達到目標角色數量條件時是否截圖 | true | true/false |

### 設定檔預設範例
```ini
[Settings]
# 需要幾個五星角色 (預設：3)
star_count = 3
# 需要幾個目標角色 (預設：1)
target_count = 1
# 是否在找到五星時截圖
save_star_screenshot = true
# 是否在找到目標角色時截圖
save_target_screenshot = true
```
在此預設值中，腳本會在達到3(含以上)個五星角色後，繼續檢查模板中是否存在1(含以上)個指定的角色模板。
請自行調整設定檔，以符合您的需求。


---

## 使用

![示例圖片](screenshot.png)
- 運行腳本。
- 等待腳本載入設定檔及圖片資訊。
- 鍵盤F9 開啟 / 停止腳本。

## 先決條件

### 安裝Python

下載並安裝Python，請訪問[Python官方網站](https://www.python.org)並根據您的操作系統下載合適的版本。安裝時請勾選“Add Python to PATH”選項。

在運行此腳本之前，請確保您的系統中安裝了以下Python庫：

- `opencv-python`
- `numpy`
- `pyautogui`
- `keyboard`
- `pillow`
- `pyautogui`

您可以使用以下命令來安裝這些庫：

```
pip install opencv-python numpy pyautogui keyboard pillow pyautogui
```
## 運行腳本
在包含上述文件的目錄中打開命令提示符或終端。輸入以下命令來運行腳本：
```
python template_matching.py
```

## 腳本邏輯 
1. 等待腳本載入設定檔及圖片資訊後，按下F9開始運行
2. 運行過程中，如果想要停止運行，請再次按下F9鍵。
3. 運行過程中，如果有符合的條件達成，腳本會自行停止，並擷取截圖。