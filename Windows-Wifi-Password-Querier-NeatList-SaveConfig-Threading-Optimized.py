from subprocess import Popen,PIPE
from sys import exit
from concurrent.futures import ThreadPoolExecutor, as_completed
import os,re,json,platform



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
    os.system("cls && color a")
    
    global TEMP_PATH,JSON_FILE_PATH,OutPrintPauseLenList,WlanNameList
    TEMP_PATH = os.path.expandvars("%TEMP%")
    JSON_FILE_PATH = os.path.join(TEMP_PATH, "wifi_config.json")
    
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
        if not os.path.exists(JSON_FILE_PATH):
            open(JSON_FILE_PATH, 'x').close()#使用open()来创建文件...别问我为什么不用os.makedirs()
            pass
        
        Wifi_Config_List = [
            {"Name":i[0], "Password":i[-1]} for i in zip(WifiName,WifiPassword)
            ]
        
        with open(JSON_FILE_PATH, 'w') as json_file:
            json.dump(Wifi_Config_List, json_file, indent=4)
            print(f"\nJSON file has been created or modified at: {JSON_FILE_PATH}")
            pass
        json_file.close()
        
    def Read_Wifi_Config(self,WifiName):
        if not os.path.exists(JSON_FILE_PATH):#判断是否存在Config，如果没有则先使用老方法先显示WiFi密码，然后在保存到Config内
            WlanPassWordList = self.OldWay()#获取WiFi密码并输出，返回WiFi密码列表
            self.Write_Wifi_Config(sorted(WifiName),WlanPassWordList)#写Config
            
        else:
            JsonWifiName = []
            JsonWifiPassword = []
            with open(JSON_FILE_PATH, 'r') as json_file:
                try:
                    data = json.load(json_file)
                    for item in data:
                        JsonWifiName.append(item['Name'])
                        JsonWifiPassword.append(item['Password'])
                        pass
                    pass
                except:
                    WlanPassWordList = self.OldWay()#获取WiFi密码并输出，返回WiFi密码列表
                    self.Write_Wifi_Config(WifiName,WlanPassWordList)#写Config
                    return
            json_file.close()

            if JsonWifiName == WifiName:
                self.main(WifiName,JsonWifiPassword)
                pass
            else:
                WlanPassWordList = self.OldWay()
                self.Write_Wifi_Config(WifiName,WlanPassWordList)
                pass
        
            
            
            print("正在检查Wifi密码是否有变动...",end="\r")
            _,WlanPassWordList = self.get_password(WifiName)
            
            if WlanPassWordList != JsonWifiPassword:#如果有一个信息错误，便会修改json中的信息并更新界面
                self.main(WifiName,WlanPassWordList)
                self.Write_Wifi_Config(WifiName,WlanPassWordList)
                pass
        
    def main(self,WlanName,WlanPassword):
        os.system("cls && color a")
        print("设备上保存的Wi-Fi信息↓\n")
        for index,(name,pwd) in enumerate(zip(WlanName,WlanPassword)):
            lon = len(list(str(len(WlanName))))+1 - len(list(str(index+1)))
            padding = OutPrintPauseLenList[index]
            print(f'{index+1}{" "*lon}"{name}"{" " * padding}密码: {pwd.strip() if pwd != "None" else "无密码"}')
        return
    
    def OldWay(self):
        
        print("正在获取本机WI-FI密码...")
    
        WlanPassWordDictionary,WlanPassWordList = self.get_password(WlanNameList)#调用方法获取wifi密码
            
        os.system("cls")
        print("设备上保存的Wi-Fi信息↓\n")
        for index,(name,pwd) in enumerate(zip(WlanNameList,WlanPassWordDictionary.items())):
            lon = len(list(str(len(WlanNameList))))+1 - len(list(str(index+1)))
            padding = OutPrintPauseLenList[index]
            print(f'{index+1}{" "*lon}"{name}"{" " * padding}密码: {pwd[-1] if pwd[-1] != "None" else "无密码"}')
            pass
        return WlanPassWordList
    pass



if __name__ == "__main__":
    if platform.system() == "Linux":
        exit()
    else:
        Main()
        os.system("pause")
        pass