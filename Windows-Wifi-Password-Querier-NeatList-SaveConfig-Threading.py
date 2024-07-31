from subprocess import Popen,PIPE
import os,re,json,platform,threading



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
    
    WlanNameList = sorted(WlanNameList)
    
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
    
    def get_password(self,WifiNameList):
        def get_password(WlanPassWordDictionary, WlanNane, WlanPassWordList):
            WlanPassWord = Popen('netsh wlan show profile "{}" key=clear | findstr "Key Content:"'.format(WlanNane),
                                    shell=True,stdout=PIPE,stderr=PIPE).communicate()[0].decode('utf-8').strip()
            match = re.search(":(.*)",WlanPassWord)#匹配字符串
            if match == None:
                WlanPassWordDictionary[WlanNane] = "未能获取到密碼"
                WlanPassWordList.append("None")
                pass
            elif match.group(1).strip() == "1": 
                WlanPassWordDictionary[WlanNane] = "无密码"
                WlanPassWordList.append("None")
                pass
            else: 
                WlanPassWordDictionary[WlanNane] = match.group(1).strip()
                WlanPassWordList.append(match.group(1).strip())
                pass
            pass
        
        thread_list = []
        WlanPassWordList = []
        WlanPassWordDictionary = {}
        lock = threading.Lock()  # 用于保护对 results 字典的访问
        
        for i in WifiNameList:
            t = threading.Thread(target=get_password, args=(WlanPassWordDictionary, i, WlanPassWordList))
            thread_list.append(t)
            pass
        
        # 启动所有线程
        for t in thread_list:
            t.start()
        # 等待所有线程完成
        for t in thread_list:
            t.join()
            pass
        
        WlanPassWordList = [WlanPassWordDictionary[i] for i in WifiNameList]
        WlanPassWordDictionary = {k: v for k,v in zip(WifiNameList,WlanPassWordList)}
        
        return WlanPassWordDictionary,WlanPassWordList
            
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
        for index,i in enumerate(zip(WlanName,WlanPassword)):
            if i[-1] == "None":
                WlanPassWord="无密码"
            else: 
                WlanPassWord=i[-1].strip()
                pass
            pass
            
            lon = len(list(str(len(WlanName)))) - len(list(str(index+1)))
            print("{0} {1}".format(str(index+1)," "*lon)
                  +'"{0}"{1}密码:{2}'.format(i[0],OutPrintPauseLenList[index]*" ",WlanPassWord))
            pass
        return
    
    def OldWay(self):
        
        print("正在获取本机WI-FI密码...")
    
        WlanPassWordDictionary,WlanPassWordList = self.get_password(WlanNameList)#调用方法获取wifi密码
            
        os.system("cls")
        print("设备上保存的Wi-Fi信息↓\n")
        for index,i in enumerate(zip(WlanNameList,WlanPassWordDictionary.items())):
            lon = len(list(str(len(i[0])))) - len(list(str(index+1)))
            print("{0} {1}".format(str(index+1)," "*lon)
                  +'"{0}"{1}密码:{2}'.format(i[0],OutPrintPauseLenList[index]*" ",i[-1][-1]))
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