from cobra.mit.access import MoDirectory
from cobra.mit.session import LoginSession
import easygui



Url =easygui.enterbox(msg = "What is the IP address of your APIC?")
user = easygui.enterbox(msg = "What is the username")
password = easygui.passwordbox(msg="please enter the password")
#Url = raw_input("What is the IP address of your APIC?")
print user
print password
apicUrl = 'https://'+ Url
try:
    loginSession = LoginSession(apicUrl, str(user), str(password))
    moDir = MoDirectory(loginSession)
    moDir.login()
except:
    easygui.msgbox("The URL and/or Credentials you entered did not work ")
    sys.exit()

easygui.msgbox("We have successfully logged into the APIC! Cobra SDK has successfully been installed")