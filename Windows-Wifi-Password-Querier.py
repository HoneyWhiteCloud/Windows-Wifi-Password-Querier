from subprocess import Popen,PIPE
import os,re

class Main(object):
    def __init__(self):
        self.main()
        pass
    def main(self):
        os.system("chcp 65001 && cls")#设置活动代码页，防止匹配信息错误
        print("正在获取本机WI-FI密码...")
        
        WlanInfo = Popen("netsh wlan show profile",shell=True,stdout=PIPE,stderr=PIPE).communicate()[0].decode('utf-8').strip().split("\n")

        WlanName = []
        WlanPassWordList = []
        
        for i in WlanInfo[1:-1]:
            match = re.search(":(.*)",i)
            try:
                WlanName.append(match.group(1).strip())
                pass
            except AttributeError:
                pass
            pass
        
        for i in WlanName:
            WlanPassWord = Popen('netsh wlan show profile "{}" key=clear | findstr "Key Content:"'.format(i),shell=True,stdout=PIPE,stderr=PIPE).communicate()[0].decode('utf-8').strip()
            
            match = re.search(":(.*)",WlanPassWord)#匹配字符串
            
            if match.group(1).strip() == "1": 
                WlanPassWordList.append("无密码")
                pass
            else: 
                WlanPassWordList.append(match.group(1).strip())
                pass
            pass
        
        os.system("cls && color a")
        print("设备上保存的Wi-Fi信息↓\n")
        for index,i in enumerate(zip(WlanName,WlanPassWordList)):
            print(index+1,'"{0}"    密码:{1}'.format(i[0],i[-1]))
            pass
        pass
    pass

if __name__ == "__main__":
    Main()
    os.system("pause")
    pass
