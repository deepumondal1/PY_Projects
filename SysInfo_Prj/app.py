import wmi
import win32com.client
import winreg
import smtplib
import pathlib
import math
from win32com.client import CDispatch
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


HTMLBody = ''
filename = ''
vbCrLf = "\n"
loc:CDispatch = win32com.client.Dispatch("WbemScripting.SWbemLocator")
svc = loc.ConnectServer(".", "root\\cimv2")
objWMIService = wmi.WMI(wmi=svc)
colItems = objWMIService.Win32_ComputerSystem()
winObjName = "ComputerSystem"
for objItem in colItems:
    uname:str = objItem.UserName
    uname = uname[uname.find("\\")+1:]
    filename = filename + uname
    HTMLBody = HTMLBody + winObjName + "|Domain|" + objItem.Domain + vbCrLf
    HTMLBody = HTMLBody + winObjName + "|UserName|" + objItem.UserName + vbCrLf
    HTMLBody = HTMLBody + winObjName + "|Name|" + objItem.Name + vbCrLf
    HTMLBody = HTMLBody + winObjName + "|Manufacturer|" + objItem.Manufacturer + vbCrLf
    HTMLBody = HTMLBody + winObjName + "|Model|" + objItem.Model + vbCrLf
    HTMLBody = HTMLBody + winObjName + "|SystemType|" + objItem.SystemType + vbCrLf
    HTMLBody = HTMLBody + winObjName + "|Status|" + objItem.Status + vbCrLf

# -------------------------------------------------------------------------------

colItems = objWMIService.Win32_OperatingSystem()
winObjName = "OperatingSystem"
for objItem in colItems:
    HTMLBody = HTMLBody + winObjName + "|Name|" + objItem.Name + vbCrLf

# -------------------------------------------------------------------------------

colItems = objWMIService.Win32_SystemEnclosure()
winObjName = "System"
for objItem in colItems:
    filename = filename + "_" + objItem.SerialNumber
    HTMLBody = HTMLBody + winObjName + "|Serial Number|" + objItem.SerialNumber + vbCrLf

# -------------------------------------------------------------------------------

colItems = objWMIService.Win32_PhysicalMemory()
winObjName = "Memory"
for objItem in colItems:
    text = f"{objItem.SerialNumber} # {objItem.Capacity} # {objItem.Speed} # {objItem.PartNumber}"
    HTMLBody = HTMLBody + winObjName + "|SerialNo # Capacity # Speed # PartNo|" + text + vbCrLf

# -------------------------------------------------------------------------------

colItems = objWMIService.Win32_DiskDrive()
winObjName = "DiskDrive"
for objItem in colItems:
    text = f"{objItem.Model}  # {(int(objItem.Size) / 1000000000):.3f} GB # {str(objItem.Partitions)}"
    HTMLBody = HTMLBody + winObjName + "|Model # Size # Partition|" + text + vbCrLf

# -------------------------------------------------------------------------------

# colItems = objWMIService.ExecQuery("Select * from Win32_NetworkAdapterConfiguration where macaddress is not null")
colItems = objWMIService.query("Select * from Win32_NetworkAdapterConfiguration where macaddress is not null")
winObjName = "Network"
for objItem in colItems:
    HTMLBody = HTMLBody + winObjName + "|Description|" + objItem.Description + vbCrLf
    if objItem.IPAddress is not None :
        HTMLBody = HTMLBody + winObjName + "|IPAddress|" + objItem.IPAddress[0] + vbCrLf
    else:
        HTMLBody = HTMLBody + winObjName + "|IPAddress|" + vbCrLf
            
    HTMLBody = HTMLBody + winObjName + "|MACAddress|" + objItem.MACAddress + vbCrLf

# -------------------------------------------------------------------------------

winObjName = "Products"
hklm_key = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
main_key_paths = [r'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall', r'SOFTWARE\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall']
for k in main_key_paths:
    uninstall_key = winreg.OpenKeyEx(hklm_key, k, 0, winreg.KEY_READ)
    # a = winreg.QueryValueEx(regObj, "DisplayName")
    i = 0
    while True:
        try:
            subkey = winreg.EnumKey(uninstall_key, i)
            # print(subkey)
            program_key = winreg.OpenKeyEx(uninstall_key, sub_key=subkey)
            # print(program_key)
            try:
                display_name = winreg.QueryValueEx(program_key, "DisplayName")[0]
                display_version = winreg.QueryValueEx(program_key, "DisplayVersion")[0]
                HTMLBody = HTMLBody + winObjName + "|DisplayName|" + display_name + vbCrLf
                HTMLBody = HTMLBody + winObjName + "|DisplayVersion|" + display_version + vbCrLf
            except FileNotFoundError:
                pass
            winreg.CloseKey(program_key)
            i += 1
        except OSError as err:
            print(err.strerror)
            break

    winreg.CloseKey(uninstall_key)

winreg.CloseKey(hklm_key)

# -------------------------------------------------------------------------------

def smtp_send_file():

    def create_attachments(filename, content):
        p = MIMEBase("application", "octet-stream")
        p.set_payload(content)
        encoders.encode_base64(p)
        p.add_header('Content-Disposition',f"attachment; filename; filename={filename}.txt")
        return p
    
    
    server = smtplib.SMTP('smtp.gmail.com', 587)
    try:
        _from = "deepumondal1@gmail.com"
        password = "kkohrqvldujibhvx"
        _to = "biplob@kei-ind.com"
        # _from = "emailkeicontrolroom@gmail.com"
        # password = "upfuoouccapcwcps"
        # _to = "sandeep@kei-ind.com"
        subject = f"IT System Info - {filename}"
        body = f"fyi\n\nThanks"

        msg = MIMEMultipart()
        msg['From'] = _from
        msg['To'] = _to
        msg['Subject'] = subject
        msg.attach(MIMEText(body, "plain"))
        # p = MIMEBase("application", "octet-stream")
        # p.set_payload(HTMLBody)
        # encoders.encode_base64(p)
        # p.add_header('Content-Disposition',f"attachment; filename; filename={filename}.txt")
        # print(p.as_string())
        # return
        p = create_attachments(filename=f"{filename}", content=HTMLBody)
        msg.attach(p)

        server.ehlo()
        server.starttls()
        print(server)
        reply = server.login(_from, password)
        print(reply)
        server.sendmail(_from, _to, msg.as_string())
        server.quit()
        server.close()
    except Exception as err:
        print("Error")
        print(err)
        server.close()

# -------------------------------------------------------------------------------

# HTMLBody = 'test body\ntestbody2'
# filename = 'test'
folder = "\\\\keibhdfile01\\commonall\\ADMIN_SOFT\\ITData\\data\\"
# folder = "C:\\Users\\biplob\\Downloads\\IT\\data\\data2\\"
path = pathlib.Path(folder)
if path.is_dir():
    if path.exists():
        path = path.joinpath(filename + ".txt")
        path.write_text(HTMLBody)
    else:
        smtp_send_file()
else:
    smtp_send_file()

# smtp_send_file()

# -------------------------------------------------------------------------------


# print(HTMLBody)
