__author__ = 'sheastma'
__version__ = '1.0.0'

try:
    import paramiko
except ImportError:
    print 'This script requires Paramiko a third party module in python'
import sys
import threading
global leafs,apics
leafs = []
#apics = []
#nodes
def get_creds():
    f = open('C:\creds.csv','rb')
    scp_url =  f.readline()
    scp_pwd =  f.readline()
    node_ip =  f.readline()
    fab_username =  f.readline()
    fab_pwd =  f.readline()
    scp_url = scp_url.split(',')[1]
    scp_pwd = scp_pwd.split(',')[1]
    fab_username = fab_username.split(',')[1]
    fab_pwd = fab_pwd.split(',')[1]
    node_ip = node_ip.split(',')[1:]

    return scp_url,scp_pwd,fab_username,fab_pwd,node_ip

def workon(host, username,password, scp_url, scp_user,scp_pass):
    #command = 'sshpass -p '+scp_pass+' scp -v -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null '+ scp_url+' /bootflash/ ; cd bootflash/ ; setup-bootvars.sh '+scp_url[scp_url.rfind("/")+1:]+' ; setup-clean-config.sh ; vsh -c "reload"'
    command = 'acidiag avread'
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=username, password=password)
    stdin, stdout, stderr = ssh.exec_command(command)
    print 'Upgrading IP address '+host
    for line in stdout:
        print host + ': ' +line

    print '__________________________________________________________________________________________________________'

def main():
    scp_url,scp_pwd,fab_username,fab_pwd,node_ip = get_creds()
    scp_user = ''
    threads = []
    for ip in node_ip:
        #bug fix - workaround
        ip = ip.rstrip()
        print 'IP '+ ip + ' is being added into the thread'
        t = threading.Thread(target=workon, args=(ip,fab_username,fab_pwd, scp_url,scp_user, scp_pwd,))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
if __name__ == "__main__":
    try:
	    main()
    except:
        print sys.exc_info()[0]

