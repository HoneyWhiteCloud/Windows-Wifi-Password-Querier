from subprocess import Popen,PIPE
import os,re,platform



##在python中，中文等字符是按照两个英文半角字符的大小进行输出的，因此需要转换成utf-8编码后再进行换算
##下列为示范代码↓
##
##txt = "名字12" 
##lenTxt = len(txt) 
##lenTxt_utf8 = len(txt.encode('utf-8')) 
##size = int((lenTxt_utf8 - lenTxt)/2 + lenTxt)
##print("size = " , size ," ,urf8 = ",lenTxt_utf8," ,len = " ,lenTxt)


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

        WlanName = []
        
        for i in WlanInfo[1:-1]:
            match = re.search(":(.*)",i)
            try:
                WlanName.append(match.group(1).strip())
                pass
            except AttributeError:
                pass
            pass
        
        utf8_WifiNameList = [len(i.encode('utf-8')) for i in WlanName]
        PauselenList = []
        for i in zip(utf8_WifiNameList,WlanName):
            PauselenList.append(int(len(i[-1])+(i[0]-len(i[-1]))/2))
            pass
        
        PauseStandard = max(PauselenList)+5#5为最低间隔长度，可任意修改
        
        OutPrintPauseLenList = []
        for i in PauselenList:
            OutPrintPauseLenList.append(PauseStandard-i)
            pass
        
        os.system("cls")
        print("设备上保存的Wi-Fi信息↓\n")
        for index,wlan_name in enumerate(WlanName):
            
            output = Popen(f'netsh wlan show profile name="{wlan_name}" key=clear',
                                 shell=True,stdout=PIPE,stderr=PIPE).communicate()[0].decode('utf-8').strip()
            match = re.search(r"^\s*Key Content\s*:\s*(.*)$", output, re.MULTILINE)
            
            if match == None or match.group(1).strip() == "1":
                WlanPassWord="无密码"
                pass
            else: 
                WlanPassWord=match.group(1).strip()
                pass
            pass
        
            lon = len(list(str(len(WlanName)))) - len(list(str(index+1)))
            print("{0} {1}".format(str(index+1)," "*lon)
                  +'"{0}"{1}密码:{2}'.format(wlan_name,OutPrintPauseLenList[index]*" ",WlanPassWord))
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