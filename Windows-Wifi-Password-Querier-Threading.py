from subprocess import Popen,PIPE
import os,re,platform,threading

class Main(object):
    def __init__(self):
        self.main()
        pass
            
    def main(self):
        os.system("chcp 65001 && cls")#设置活动代码页，防止匹配信息错误
        os.system("cls && color a")
        
        print("正在获取本机WI-FI密码...")
        
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
        
        def get_password(WlanPassWordDictionary, WlanNane):
            WlanPassWord = Popen('netsh wlan show profile "{}" key=clear | findstr "Key Content:"'.format(WlanNane),
                                    shell=True,stdout=PIPE,stderr=PIPE).communicate()[0].decode('utf-8').strip()
            match = re.search(":(.*)",WlanPassWord)#匹配字符串
            if match == None:
                WlanPassWordDictionary[WlanNane] = "未能获取到密碼"
                pass
            elif match.group(1).strip() == "1": 
                WlanPassWordDictionary[WlanNane] = "无密码"
                pass
            else: 
                WlanPassWordDictionary[WlanNane] = match.group(1).strip()
                pass
            pass
        
        thread_list = []
        WlanPassWordDictionary = {}
        lock = threading.Lock()  # 用于保护对 results 字典的访问
        
        for i in WlanNameList:
            t = threading.Thread(target=get_password, args=(WlanPassWordDictionary, i,))
            thread_list.append(t)
         # 启动所有线程
        for t in thread_list:
            t.start()

        # 等待所有线程完成
        for t in thread_list:
            t.join()
            
        os.system("cls")
        print("设备上保存的Wi-Fi信息↓\n")
        for index,i in enumerate(WlanPassWordDictionary.items()):
            print(index+1,'"{0}"    密码:{1}'.format(i[0],i[-1]))
            pass
        pass
    pass

if __name__ == "__main__":
    if platform.system() == "Linux":
        exit()
    else:
        Main()
        os.system("pause")
        pass
