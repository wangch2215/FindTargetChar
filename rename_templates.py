import os
import re

def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

def rename_templates():
    templates_dir = os.path.join(os.getcwd(), "templates")

    if not os.path.exists(templates_dir):
        print("templates 資料夾不存在！請確認路徑。")
        return

    files = [f for f in os.listdir(templates_dir)
             if os.path.isfile(os.path.join(templates_dir, f)) and f.lower().endswith('.png')]

    files.sort(key=natural_sort_key)

    temp_names = []
    for idx, file in enumerate(files, start=1):
        old_path = os.path.join(templates_dir, file)
        temp_name = f"temp_{idx}.tmp"
        temp_path = os.path.join(templates_dir, temp_name)
        os.rename(old_path, temp_path)
        temp_names.append(temp_path)

    for idx, temp_path in enumerate(temp_names, start=1):
        new_name = f"t{idx}.png"
        new_path = os.path.join(templates_dir, new_name)
        os.rename(temp_path, new_path)
        print(f"已重新命名: {os.path.basename(temp_path)} -> {new_name}")

if __name__ == "__main__":
    rename_templates()
