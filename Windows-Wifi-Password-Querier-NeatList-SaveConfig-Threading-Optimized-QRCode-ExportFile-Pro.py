from subprocess import Popen,PIPE
from sys import exit
from concurrent.futures import ThreadPoolExecutor, as_completed
import os,re,json,platform
import importlib.util
import subprocess
import sys
import base64
from datetime import datetime


##在python中，中文等字符是按照两个英文半角字符的大小进行输出的，因此需要转换成utf-8编码后再进行换算
##下列为示范代码↓
##
##txt = "名字12" 
##lenTxt = len(txt) 
##lenTxt_utf8 = len(txt.encode('utf-8')) 
##size = int((lenTxt_utf8 - lenTxt)/2 + lenTxt)
##print("size = " , size ," ,urf8 = ",lenTxt_utf8," ,len = " ,lenTxt)


class Main(object):
    os.system("chcp 65001 && cls")#设置活动代码页，防止匹配信息错误
    os.system("color a")
    
    global TEMP_PATH,JSON_FILE_PATH,OutPrintPauseLenList,WlanNameList,ENABLE_ENCRYPTION,ENCRYPTION_CONFIG_FILE
    TEMP_PATH = os.path.expandvars("%TEMP%")
    JSON_FILE_PATH = os.path.join(TEMP_PATH, "wifi_config.json")
    ENCRYPTION_CONFIG_FILE = os.path.join(TEMP_PATH, "wifi_encryption.conf")
    
    # 读取加密配置
    ENABLE_ENCRYPTION = False
    if os.path.exists(ENCRYPTION_CONFIG_FILE):
        try:
            with open(ENCRYPTION_CONFIG_FILE, 'r') as f:
                ENABLE_ENCRYPTION = f.read().strip() == 'True'
        except:
            pass
    
    WlanInfo = Popen("netsh wlan show profile",
                     shell=True,stdout=PIPE,stderr=PIPE).communicate()[0].decode('utf-8').strip().split("\n")
    WlanNameList = []
    for i in WlanInfo[1:-1]:
        match = re.search(":(.*)",i)
        try:
            WlanNameList.append(match.group(1).strip())
            pass
        except AttributeError:
            pass
        pass
    
    WlanNameList = sorted(WlanNameList)#按照名称对所有WIFI排列
    
    utf8_WifiNameList = [len(i.encode('utf-8')) for i in WlanNameList]
    PauselenList = []
    for i in zip(utf8_WifiNameList,WlanNameList):
        PauselenList.append(int(len(i[-1])+(i[0]-len(i[-1]))/2))
        pass
    if PauselenList:#检测是否为空列表，如果为空则电脑上没有wifi信息
        PauseStandard = max(PauselenList)+5#5为最低间隔长度，可任意修改
        pass
    else:
        os.system("cls")
        print("此电脑上没有保存任何Wifi密码!")
        os.system("pause")
        exit()
        
    OutPrintPauseLenList = []
    for i in PauselenList:
        OutPrintPauseLenList.append(PauseStandard-i)
        pass
    
    def save_encryption_config(self):
        """保存加密配置"""
        with open(ENCRYPTION_CONFIG_FILE, 'w') as f:
            f.write(str(ENABLE_ENCRYPTION))
    
    def evaluate_password_strength(self, password):
        """评估密码强度，返回分数(0-100)和等级"""
        if not password or password in ["未能获取到密码", "无密码", "None"]:
            return 0, "无密码", ""
        
        score = 0
        feedback = []
        
        # 长度评分 (最高30分)
        length = len(password)
        if length >= 12:
            score += 30
        elif length >= 8:
            score += 20
        elif length >= 6:
            score += 10
        else:
            score += 5
            feedback.append("密码过短")
        
        # 字符类型评分 (最高40分)
        has_lower = bool(re.search(r'[a-z]', password))
        has_upper = bool(re.search(r'[A-Z]', password))
        has_digit = bool(re.search(r'\d', password))
        has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
        
        char_types = sum([has_lower, has_upper, has_digit, has_special])
        score += char_types * 10
        
        if not has_lower and not has_upper:
            feedback.append("缺少字母")
        if not has_digit:
            feedback.append("缺少数字")
        if not has_special:
            feedback.append("缺少特殊字符")
        
        # 复杂度评分 (最高30分)
        # 检查是否有连续字符
        if not re.search(r'(.)\1{2,}', password):  # 没有连续重复字符
            score += 10
        else:
            feedback.append("包含重复字符")
        
        # 检查是否为常见模式
        common_patterns = ['123', '321', 'abc', 'qwe', '111', '000', 'aaa']
        if not any(pattern in password.lower() for pattern in common_patterns):
            score += 10
        else:
            feedback.append("包含常见模式")
        
        # 检查是否全为数字或全为字母
        if not (password.isdigit() or password.isalpha()):
            score += 10
        
        # 确定强度等级
        if score >= 80:
            level = "强"
            color = "green"
        elif score >= 60:
            level = "中"
            color = "yellow"
        elif score >= 40:
            level = "弱"
            color = "orange"
        else:
            level = "极弱"
            color = "red"
        
        return score, level, color
    
    def get_strength_bar(self, score, width=20, for_terminal=True):
        """生成强度条（不使用颜色）"""
        filled = int(score / 100 * width)
        empty = width - filled
        
        if for_terminal:
            # 终端显示 - 使用不同字符表示强度
            if score >= 80:
                bar = "█" * filled + "░" * empty
            elif score >= 60:
                bar = "▓" * filled + "░" * empty
            elif score >= 40:
                bar = "▒" * filled + "░" * empty
            else:
                bar = "░" * filled + "·" * empty
            return bar
        else:
            # HTML显示保持不变
            if score >= 80:
                color = "#4CAF50"
            elif score >= 60:
                color = "#FFC107"
            elif score >= 40:
                color = "#FF9800"
            else:
                color = "#F44336"
            
            return f"""
            <div style="width: 200px; height: 20px; background-color: #ddd; border-radius: 10px; overflow: hidden;">
                <div style="width: {score}%; height: 100%; background-color: {color}; transition: width 0.3s;"></div>
            </div>
            """
    
    def simple_encrypt(self, text):
        """简单的密码加密（基于Base64和位移）"""
        if not text or text in ["未能获取到密码", "无密码", "None"]:
            return text
        
        # 先进行简单的字符位移
        shifted = ''.join(chr((ord(char) + 7) % 256) for char in text)
        # 然后base64编码
        encrypted = base64.b64encode(shifted.encode('utf-8')).decode('utf-8')
        return encrypted
    
    def simple_decrypt(self, encrypted_text):
        """简单的密码解密"""
        if not encrypted_text or encrypted_text in ["未能获取到密码", "无密码", "None"]:
            return encrypted_text
        
        try:
            # 先base64解码
            decoded = base64.b64decode(encrypted_text.encode('utf-8')).decode('utf-8')
            # 然后进行字符位移还原
            decrypted = ''.join(chr((ord(char) - 7) % 256) for char in decoded)
            return decrypted
        except:
            # 如果解密失败，返回原文（可能是未加密的旧数据）
            return encrypted_text
    
    def export_wifi_data(self, WlanName, WlanPassword):
        """导出WiFi数据到文件"""
        os.system("cls")
        print("╔" + "═" * 54 + "╗")
        print("║" + self.center_text("导出WiFi信息", 52) + "║")
        print("╚" + "═" * 54 + "╝")
        
        print("\n选择导出格式：")
        print("1. TXT文本文件")
        print("2. CSV表格文件")
        print("3. HTML网页文件（推荐）")
        print("4. JSON数据文件")
        print("0. 返回")
        
        choice = input("\n请选择导出格式: ")
        
        if choice == '0':
            return
        
        # 询问是否包含密码
        include_pwd = input("\n是否包含密码信息？(y/n): ").lower() == 'y'
        include_strength = False
        if include_pwd:
            include_strength = input("是否包含密码强度评估？(y/n): ").lower() == 'y'
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        
        try:
            if choice == '1':  # TXT
                filename = os.path.join(desktop_path, f"WiFi_Info_{timestamp}.txt")
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write("="*60 + "\n")
                    f.write(f"WiFi信息导出 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("="*60 + "\n\n")
                    
                    for i, (name, pwd) in enumerate(zip(WlanName, WlanPassword), 1):
                        f.write(f"【{i}】 WiFi名称: {name}\n")
                        if include_pwd:
                            f.write(f"     密码: {pwd}\n")
                            if include_strength:
                                score, level, _ = self.evaluate_password_strength(pwd)
                                bar = "█" * int(score/5) + "░" * (20-int(score/5))
                                f.write(f"     强度: {level} [{bar}] {score}分\n")
                        f.write("-"*40 + "\n")
                    
                    f.write(f"\n共导出 {len(WlanName)} 个WiFi信息\n")
                
            elif choice == '2':  # CSV
                filename = os.path.join(desktop_path, f"WiFi_Info_{timestamp}.csv")
                with open(filename, 'w', encoding='utf-8-sig') as f:
                    headers = ["序号", "WiFi名称"]
                    if include_pwd:
                        headers.append("密码")
                        if include_strength:
                            headers.extend(["强度等级", "强度分数"])
                    
                    f.write(",".join(headers) + "\n")
                    
                    for i, (name, pwd) in enumerate(zip(WlanName, WlanPassword), 1):
                        row = [str(i), f'"{name}"']
                        if include_pwd:
                            row.append(f'"{pwd}"')
                            if include_strength:
                                score, level, _ = self.evaluate_password_strength(pwd)
                                row.extend([level, str(score)])
                        f.write(",".join(row) + "\n")
            
            elif choice == '3':  # HTML
                filename = os.path.join(desktop_path, f"WiFi_Info_{timestamp}.html")
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write("""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>WiFi信息列表</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 20px; 
            background-color: #f5f5f5; 
        }
        h1 { 
            color: #333; 
            text-align: center; 
        }
        table { 
            border-collapse: collapse; 
            width: 100%; 
            max-width: 1000px; 
            margin: 0 auto; 
            background-color: white; 
            box-shadow: 0 2px 4px rgba(0,0,0,0.1); 
        }
        th, td { 
            border: 1px solid #ddd; 
            padding: 12px; 
            text-align: left; 
        }
        th { 
            background-color: #4CAF50; 
            color: white; 
        }
        tr:nth-child(even) { 
            background-color: #f9f9f9; 
        }
        .footer { 
            text-align: center; 
            margin-top: 20px; 
            color: #666; 
        }
        .strength-bar {
            width: 150px;
            height: 20px;
            background-color: #ddd;
            border-radius: 10px;
            overflow: hidden;
            display: inline-block;
            vertical-align: middle;
        }
        .strength-fill {
            height: 100%;
            transition: width 0.3s;
        }
        .strength-strong { background-color: #4CAF50; }
        .strength-medium { background-color: #FFC107; }
        .strength-weak { background-color: #FF9800; }
        .strength-very-weak { background-color: #F44336; }
        .strength-text {
            display: inline-block;
            margin-left: 10px;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <h1>WiFi信息列表</h1>
    <table>
        <tr>
            <th width="5%">序号</th>
            <th width="25%">WiFi名称</th>
""")
                    if include_pwd:
                        f.write('            <th width="25%">密码</th>\n')
                        if include_strength:
                            f.write('            <th width="45%">密码强度</th>\n')
                    f.write("        </tr>\n")
                    
                    for i, (name, pwd) in enumerate(zip(WlanName, WlanPassword), 1):
                        f.write(f"        <tr>\n")
                        f.write(f"            <td>{i}</td>\n")
                        f.write(f"            <td>{name}</td>\n")
                        if include_pwd:
                            f.write(f"            <td>{pwd}</td>\n")
                            if include_strength:
                                score, level, color = self.evaluate_password_strength(pwd)
                                if score > 0:
                                    strength_class = ""
                                    if score >= 80:
                                        strength_class = "strength-strong"
                                    elif score >= 60:
                                        strength_class = "strength-medium"
                                    elif score >= 40:
                                        strength_class = "strength-weak"
                                    else:
                                        strength_class = "strength-very-weak"
                                    
                                    f.write(f"""            <td>
                <div class="strength-bar">
                    <div class="strength-fill {strength_class}" style="width: {score}%;"></div>
                </div>
                <span class="strength-text" style="color: {color};">{level} ({score}分)</span>
            </td>\n""")
                                else:
                                    f.write(f"            <td>无密码</td>\n")
                        f.write(f"        </tr>\n")
                    
                    f.write(f"""    </table>
    <div class="footer">
        <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>共 {len(WlanName)} 个WiFi信息</p>
    </div>
</body>
</html>""")
            
            elif choice == '4':  # JSON
                filename = os.path.join(desktop_path, f"WiFi_Info_{timestamp}.json")
                data = {
                    "export_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "total_count": len(WlanName),
                    "wifi_list": []
                }
                
                for i, (name, pwd) in enumerate(zip(WlanName, WlanPassword), 1):
                    wifi_item = {
                        "index": i,
                        "name": name
                    }
                    if include_pwd:
                        wifi_item["password"] = pwd
                        if include_strength:
                            score, level, _ = self.evaluate_password_strength(pwd)
                            wifi_item["strength"] = {
                                "score": score,
                                "level": level
                            }
                    data["wifi_list"].append(wifi_item)
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
            
            else:
                print("无效的选择")
                return
            
            print(f"\n✓ 文件已成功导出到桌面: {os.path.basename(filename)}")
            
        except Exception as e:
            print(f"\n✗ 导出失败: {str(e)}")
        
        input("\n按回车键返回...")
    
    def toggle_encryption(self):
        """切换加密状态"""
        global ENABLE_ENCRYPTION
        os.system("cls")
        print("╔" + "═" * 54 + "╗")
        print("║" + self.center_text("密码加密设置", 52) + "║")
        print("╚" + "═" * 54 + "╝")
        
        current_status = "已启用" if ENABLE_ENCRYPTION else "已禁用"
        print(f"\n当前加密状态: {current_status}")
        
        if not ENABLE_ENCRYPTION:
            print("\n启用加密将对JSON文件中的密码进行加密存储")
            print("注意：启用后需要重新获取一次WiFi密码")
            choice = input("\n是否启用加密？(y/n): ").lower()
            
            if choice == 'y':
                ENABLE_ENCRYPTION = True
                self.save_encryption_config()
                print("\n✓ 加密已启用")
                # 清除现有配置文件，强制重新获取
                if os.path.exists(JSON_FILE_PATH):
                    os.remove(JSON_FILE_PATH)
                    print("已清除旧配置文件，将重新获取WiFi信息...")
        else:
            print("\n禁用加密将以明文形式存储密码")
            choice = input("\n是否禁用加密？(y/n): ").lower()
            
            if choice == 'y':
                ENABLE_ENCRYPTION = False
                self.save_encryption_config()
                print("\n✓ 加密已禁用")
                # 清除现有配置文件，强制重新获取
                if os.path.exists(JSON_FILE_PATH):
                    os.remove(JSON_FILE_PATH)
                    print("已清除旧配置文件，将重新获取WiFi信息...")
        
        input("\n按回车键返回...")
        return True  # 返回True表示需要重新初始化
    
    def get_display_width(self, text):
        """计算文本的显示宽度（考虑中文字符）"""
        width = 0
        for char in text:
            if '\u4e00' <= char <= '\u9fff':  # 中文字符范围
                width += 2
            else:
                width += 1
        return width
    
    def center_text(self, text, total_width):
        """将文本居中对齐（考虑中文字符宽度）"""
        text_width = self.get_display_width(text)
        if text_width >= total_width:
            return text
        
        padding = total_width - text_width
        left_padding = padding // 2
        right_padding = padding - left_padding
        
        return ' ' * left_padding + text + ' ' * right_padding
    
    def check_and_install_package(self, package_name):
        """检查并安装所需的包"""
        spec = importlib.util.find_spec(package_name)
        if spec is None:
            print(f"\n检测到缺少 {package_name} 库")
            choice = input(f"是否自动安装 {package_name}? (y/n): ").lower()
            if choice == 'y':
                print(f"正在安装 {package_name}...")
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
                    print(f"{package_name} 安装成功!")
                    return True
                except subprocess.CalledProcessError:
                    print(f"{package_name} 安装失败，请手动运行: pip install {package_name}")
                    return False
            else:
                print("已取消安装")
                return False
        return True
    
    def generate_qr_terminal(self, ssid, password, security='WPA'):
        """在终端中直接显示WiFi二维码"""
        # 检查并安装qrcode库
        if not self.check_and_install_package('qrcode'):
            return False
            
        try:
            import qrcode
            
            # WiFi连接字符串格式
            wifi_string = f"WIFI:T:{security};S:{ssid};P:{password};;"
            
            # 创建QR码对象
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=1,
                border=2,
            )
            
            qr.add_data(wifi_string)
            qr.make(fit=True)
            
            # 清屏并显示信息
            os.system("cls")
            
            # 使用改进的居中对齐方式
            box_width = 54  # 框的总宽度
            title = "WiFi 连接二维码"
            centered_title = self.center_text(title, box_width - 2)  # -2 是因为两边的边框符号
            
            print("╔" + "═" * box_width + "╗")
            print("║" + centered_title + "║")
            print("╚" + "═" * box_width + "╝")
            
            print(f"\nWiFi名称: {ssid}")
            print(f"密码: {password}")
            
            # 显示密码强度
            score, level, _ = self.evaluate_password_strength(password)
            strength_bar = self.get_strength_bar(score, 20, True)
            print(f"密码强度: {strength_bar} {level} ({score}分)")
            
            print("\n使用手机扫描下方二维码可直接连接WiFi：\n")
            
            # 获取二维码矩阵并显示
            matrix = qr.get_matrix()
            for row in matrix:
                line = ""
                for cell in row:
                    line += "██" if cell else "  "
                print(line)
            
            print("\n提示：确保手机相机支持WiFi二维码识别")
            return True
            
        except Exception as e:
            print(f"生成二维码时出错: {str(e)}")
            return False
    
    def show_main_menu(self, WlanName, WlanPassword):
        """显示主菜单"""
        while True:
            os.system("cls && color a")
            print("设备上保存的Wi-Fi信息↓\n")
            
            # 计算强度信息的对齐
            strength_infos = []
            max_strength_width = 0
            
            for pwd in WlanPassword:
                if pwd and pwd not in ["未能获取到密码", "无密码", "None"]:
                    score, level, _ = self.evaluate_password_strength(pwd)
                    strength_bar = self.get_strength_bar(score, 10, True)
                    strength_info = f"[{strength_bar}] {level}({score:>2}分)"
                    strength_infos.append(strength_info)
                    # 计算显示宽度
                    display_width = 10 + 2 + len(level) * 2 + 7  # 进度条10 + 括号2 + 中文字符*2 + 分数部分7
                    max_strength_width = max(max_strength_width, display_width)
                else:
                    strength_infos.append("")
            
            # 显示WiFi列表
            for index,(name,pwd) in enumerate(zip(WlanName,WlanPassword)):
                lon = len(list(str(len(WlanName))))+1 - len(list(str(index+1)))
                padding = OutPrintPauseLenList[index]
                
                # 基础信息
                base_info = f'{index+1}{" "*lon}"{name}"{" " * padding}密码: {pwd.strip() if pwd != "None" else "无密码"}'
                
                # 计算密码部分的显示宽度
                pwd_display = pwd.strip() if pwd != "None" else "无密码"
                pwd_width = self.get_display_width(pwd_display)
                
                # 添加强度信息（如果有）
                if strength_infos[index]:
                    # 计算需要的空格数以对齐
                    extra_padding = 30 - pwd_width  # 假设密码最大宽度为30
                    if extra_padding < 2:
                        extra_padding = 2
                    print(f"{base_info}{' ' * extra_padding}{strength_infos[index]}")
                else:
                    print(base_info)
            
            print("\n" + "="*80)
            print("功能菜单：")
            print("1. 生成WiFi连接二维码")
            print("2. 导出WiFi信息")
            print("3. 密码加密设置")
            print("4. 刷新WiFi列表")
            print("5. 密码强度统计")
            print("0. 退出程序")
            
            choice = input("\n请选择功能: ")
            
            if choice == '0':
                break
            elif choice == '1':
                self.show_wifi_qr_submenu(WlanName, WlanPassword)
            elif choice == '2':
                self.export_wifi_data(WlanName, WlanPassword)
            elif choice == '3':
                if self.toggle_encryption():
                    return 'restart'  # 需要重启程序
            elif choice == '4':
                return 'refresh'  # 刷新WiFi列表
            elif choice == '5':
                self.show_strength_statistics(WlanName, WlanPassword)
            else:
                print("无效的选择，请重新输入")
                input("按回车键继续...")
    
    def show_strength_statistics(self, WlanName, WlanPassword):
        """显示密码强度统计"""
        os.system("cls")
        print("╔" + "═" * 54 + "╗")
        print("║" + self.center_text("密码强度统计", 52) + "║")
        print("╚" + "═" * 54 + "╝")
        
        # 统计各强度等级的数量
        strength_stats = {"强": 0, "中": 0, "弱": 0, "极弱": 0, "无密码": 0}
        total_score = 0
        valid_count = 0
        
        for pwd in WlanPassword:
            score, level, _ = self.evaluate_password_strength(pwd)
            if level == "无密码":
                strength_stats["无密码"] += 1
            else:
                strength_stats[level] += 1
                total_score += score
                valid_count += 1
        
        print(f"\n总计 {len(WlanName)} 个WiFi：")
        print("-" * 40)
        
        for level, count in strength_stats.items():
            if count > 0:
                percentage = count / len(WlanName) * 100
                bar_length = int(percentage / 5)
                
                # 使用不同字符表示不同强度
                if level == "强":
                    bar = "█" * bar_length + "░" * (20 - bar_length)
                elif level == "中":
                    bar = "▓" * bar_length + "░" * (20 - bar_length)
                elif level == "弱":
                    bar = "▒" * bar_length + "░" * (20 - bar_length)
                elif level == "极弱":
                    bar = "░" * bar_length + "·" * (20 - bar_length)
                else:
                    bar = "·" * bar_length + " " * (20 - bar_length)
                
                print(f"{level:4}: {bar} {count}个 ({percentage:.1f}%)")
        
        if valid_count > 0:
            avg_score = total_score / valid_count
            print(f"\n平均密码强度分数: {avg_score:.1f}/100")
        
        print("\n建议：")
        if strength_stats["极弱"] + strength_stats["弱"] > 0:
            print("- 部分WiFi密码强度较弱，建议更换为更复杂的密码")
        if strength_stats["无密码"] > 0:
            print("- 存在无密码的WiFi，建议设置密码以提高安全性")
        
        input("\n按回车键返回...")
    
    def show_wifi_qr_submenu(self, WlanName, WlanPassword):
        """WiFi二维码子菜单"""
        while True:
            print("\n" + "-"*50)
            print("输入WiFi序号生成连接二维码，输入0返回")
            
            try:
                choice = input("\n请选择WiFi序号: ")
                if choice == '0':
                    break
                
                index = int(choice) - 1
                if 0 <= index < len(WlanName):
                    ssid = WlanName[index]
                    password = WlanPassword[index]
                    
                    if password in ["未能获取到密码", "无密码", "None"] or not password.strip():
                        os.system("cls")
                        print(f"{ssid} 没有密码或无法生成二维码")
                        input("按回车键继续...")
                    else:
                        if self.generate_qr_terminal(ssid, password):
                            input("\n按回车键返回...")
                    
                    # 返回主菜单
                    break
                else:
                    print("无效的序号，请重新输入")
            except ValueError:
                print("请输入有效的数字")
            except KeyboardInterrupt:
                print("\n已取消操作")
                break
    
    def get_password(self, WifiNameList):
        def get_password(WlanNane):
            command = f'netsh wlan show profile "{WlanNane}" key=clear | findstr "Key Content:"'
            WlanPassWord = Popen(command, shell=True, stdout=PIPE, stderr=PIPE).communicate()[0].decode('utf-8').strip()
            match = re.search(":(.*)", WlanPassWord)

            if match is None:
                return WlanNane, "未能获取到密码"
            elif match.group(1).strip() == "1":
                return WlanNane, "无密码"
            else:
                return WlanNane, match.group(1).strip()

        WlanPassWordDictionary = {}
        
        # 使用 ThreadPoolExecutor 来处理多线程任务
        with ThreadPoolExecutor(max_workers=10) as executor:
            # 提交任务到线程池
            futures = {executor.submit(get_password, wlan_name): wlan_name for wlan_name in WifiNameList}

            # 收集任务结果
            for future in as_completed(futures):
                wlan_name, password = future.result()
                WlanPassWordDictionary[wlan_name] = password

        WlanPassWordList = [WlanPassWordDictionary.get(i, "未能获取到密码") for i in WifiNameList]
        return WlanPassWordDictionary, WlanPassWordList
            
    def __init__(self):
        self.Read_Wifi_Config(WlanNameList)
        pass
    
    def Write_Wifi_Config(self,WifiName,WifiPassword):
        """写入WiFi配置（支持加密）"""
        if not os.path.exists(JSON_FILE_PATH):
            open(JSON_FILE_PATH, 'x').close()
        
        # 如果启用了加密，对密码进行加密
        if ENABLE_ENCRYPTION:
            encrypted_passwords = [self.simple_encrypt(pwd) for pwd in WifiPassword]
            Wifi_Config_List = [
                {"Name":name, "Password":pwd, "encrypted": True} 
                for name, pwd in zip(WifiName, encrypted_passwords)
            ]
        else:
            Wifi_Config_List = [
                {"Name":name, "Password":pwd, "encrypted": False} 
                for name, pwd in zip(WifiName, WifiPassword)
            ]
        
        with open(JSON_FILE_PATH, 'w') as json_file:
            json.dump(Wifi_Config_List, json_file, indent=4)
            encryption_status = "（已加密）" if ENABLE_ENCRYPTION else "（未加密）"
            # 不在这里打印，避免干扰界面
        
    def Read_Wifi_Config(self,WifiName):
        if not os.path.exists(JSON_FILE_PATH):
            WlanPassWordList = self.OldWay()
            self.Write_Wifi_Config(sorted(WifiName),WlanPassWordList)
        else:
            JsonWifiName = []
            JsonWifiPassword = []
            is_encrypted = False
            
            with open(JSON_FILE_PATH, 'r') as json_file:
                try:
                    data = json.load(json_file)
                    for item in data:
                        JsonWifiName.append(item['Name'])
                        # 检查是否加密
                        if item.get('encrypted', False):
                            JsonWifiPassword.append(self.simple_decrypt(item['Password']))
                            is_encrypted = True
                        else:
                            JsonWifiPassword.append(item['Password'])
                except:
                    WlanPassWordList = self.OldWay()
                    self.Write_Wifi_Config(WifiName,WlanPassWordList)
                    return
            json_file.close()

            if JsonWifiName == WifiName:
                result = self.show_main_menu(WifiName, JsonWifiPassword)
                if result == 'restart':
                    os.system("cls")
                    print("正在重新启动程序...")
                    os.execv(sys.executable, ['python'] + sys.argv)
                elif result == 'refresh':
                    self.__init__()
            else:
                WlanPassWordList = self.OldWay()
                self.Write_Wifi_Config(WifiName,WlanPassWordList)
            
            # 只在加密状态不一致时才更新
            if is_encrypted != ENABLE_ENCRYPTION:
                print("\n正在更新加密状态...", end="\r")
                _,WlanPassWordList = self.get_password(WifiName)
                self.Write_Wifi_Config(WifiName, WlanPassWordList)
                
            exit()
        
    def main(self,WlanName,WlanPassword):
        """不再直接调用，改为通过主菜单调用"""
        pass
    
    def OldWay(self):
        print("正在获取本机WI-FI密码...")
        
        WlanPassWordDictionary,WlanPassWordList = self.get_password(WlanNameList)
        
        # 显示主菜单而不是简单列表
        result = self.show_main_menu(WlanNameList, WlanPassWordList)
        if result == 'restart':
            os.system("cls")
            print("正在重新启动程序...")
            os.execv(sys.executable, ['python'] + sys.argv)
        elif result == 'refresh':
            self.__init__()
        
        return WlanPassWordList



if __name__ == "__main__":
    if platform.system() == "Linux":
        exit()
    else:
        Main()
        os.system("pause")