__author__ = 'sheastma'
import requests
import paramiko
import re
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()
from Tkinter import *
import Tkinter as tk
import json

class login(tk.Frame):

    def __init__(self, Master = None):
        tk.Frame.__init__(self, Master)
        self._cookies = None
        self._ip = StringVar()
        self.dns_provide = StringVar()
        self._user = StringVar()
        self._password = StringVar()
        self._sip = StringVar()
        self._dip = StringVar()
        self._time = IntVar()
        Label(Master, text = "ip address").pack()
        Entry(Master,textvariable = self._ip ).pack()
        Label(Master, text = "username").pack()
        Entry(Master,textvariable = self._user ).pack()
        Label(Master, text = "password").pack()
        Entry(Master,show = "*",textvariable = self._password ).pack()
        Label(Master, text = "-------------------").pack()
        Label(Master, text = "   ELAM EP input").pack()
        Label(Master, text = "-------------------").pack()
        Label(Master, text = "Source EP").pack()
        Entry(Master,textvariable = self._sip ).pack()
        Label(Master, text = "Destination EP").pack()
        Entry(Master,textvariable = self._dip ).pack()
        Label(Master, text = "Time").pack()
        Entry(Master,textvariable = self._time ).pack()
        button = Button(Master,text = "ok", command = lambda: self.close_device(Master), bg = "red",fg = "blue")
        button.pack()
        Master.mainloop()
        name_pwd = {'aaaUser': {'attributes': {'name': self._user.get(), 'pwd': self._password.get()}}}
        json_credentials = json.dumps(name_pwd)
        login_url = 'https://%s/api/aaaLogin.json'%self.ip.get()

        try:
            post_response = requests.post(login_url, data=json_credentials, verify = False)
            post_response.raise_for_status()
        except requests.ConnectionError:
            self.error_message("%s The IP address you provided is incorrect.")%str(requests.ConnectionError.message)
            sys.exit()
        except requests.HTTPError, e:
            self.error_message("%s The credentials you provided are incorrect")%str(requests.HTTPError.message)
            sys.exit()

        # get token from login response structure
        auth = json.loads(post_response.text)
        login_attributes = auth['imdata'][0]['aaaLogin']['attributes']
        auth_token = login_attributes['token']
        # create cookie array from token
        cookies = {}
        cookies['APIC-Cookie'] = auth_token
        self._cookies = cookies
    def __repr__(self):
        return 'LoginInst(ip = %s, user = %s' % (self._ip,self._user)

    def error_message(self,message):
        root = Tk()
        root.title("ERROR")
        Label(root, text = message).pack()
        root.mainloop()

    #closes the tkinter GUI Application
    def close_device(self, Master):
        Master.destroy()
    #returns the token created to post and get requests to the APIC
    @property
    def cookies(self):
        return self._cookies
    @property
    def ip(self):
        return self._ip
    @property
    def user(self):
        return self._user
    @property
    def password(self):
        return self._password
    @property
    def sip(self):
        return self._sip
    @property
    def dip(self):
        return self._dip
    @property
    def time(self):
        return self._time


def message(message):
    root = Tk()
    Label(root, text = message).pack()
    root.mainloop()



def find_endpoints(ip, cookies, *args):
    endpoint_url = 'https://'+ ip.get() + '/api/node/class/fvCEp.json'
    paths_url =  'https://'+ ip.get() + '/api/node/class/fvRsCEpToPathEp.json'
    get_response = requests.get(endpoint_url,verify = False, cookies = cookies)
    get_response_2 = requests.get(paths_url,verify = False, cookies = cookies)
    response = json.loads(get_response.text)
    response_2 = json.loads(get_response_2.text)
    count = int(response["totalCount"])
    pathF = False
    paths = []
    nodes = []
    count_2 = int(response_2["totalCount"])
    if args[0]:
        for i in xrange(0,count,1):
            for j,arg in enumerate(args):
                if (arg ==response['imdata'][i]['fvCEp']['attributes']['ip']):
                    #EP.found()
                    message("Found "+arg)
                    path = {'node':'','ip':arg,'mac':response['imdata'][i]['fvCEp']['attributes']['mac'],'role':j}
                    print path
                    paths.append(path)
        message("Found "+str(len(paths))+" endpoints. ${0}".format("No Elam will be possible" if len(paths)==0 else " Finding Leafs that EP reside"))#; endstatment = "Please verify EP exists" if len(paths) ==0 ))
            #else:
             #   message("Could not find any EP with those ip addresses ")
              #  sys.exit()

        for i in xrange(0,count_2,1):
            mac = re.findall("cep-(.+)/rsc",response_2['imdata'][i]['fvRsCEpToPathEp']['attributes']['dn'])
            for path in paths:
                if mac[0] == path['mac']:
                    if re.search("paths-(.+)/pathep-\[eth",response_2['imdata'][i]['fvRsCEpToPathEp']['attributes']['tDn']):
                        node =re.findall("paths-(.+)/pathep-\[eth",response_2['imdata'][i]['fvRsCEpToPathEp']['attributes']['tDn'])
                        path['node'] = node[0]
                        #nodes.append(node)
        return paths

def find_leafs(ip, cookies):
    leaf_url = 'https://'+ ip.get() + '/api/node/class/topSystem.json'
    get_response = requests.get(leaf_url,verify = False, cookies = cookies)
    response = json.loads(get_response.text)
    print response
    count = int(response["totalCount"])
    leafs = []

    for i in range(0,count,1):
        if response['imdata'][i]['topSystem']['attributes']['role'] == 'leaf':
            temp = {'name':response['imdata'][i]['topSystem']['attributes']['name'],
             'node':response['imdata'][i]['topSystem']['attributes']['id'],
             'oob':response['imdata'][i]['topSystem']['attributes']['oobMgmtAddr']}
            print temp
            leafs.append(temp)
    return leafs

def elam(**kwargs):

    message('ELAM capture will be open for '+str(kwargs['time']) + ' seconds. text file will have all the contents of the capture')
    #command = "acidiag fnvread"
    if kwargs['dir'] == 'source':

        command = 'vsh_lc -c "debug platform internal ns elam asic 0 ;' \
                ' trigger init ingress in-select 3 out-select 0 ;' \
                ' set outer ipv4 src_ip '+kwargs['source']+' dst_ip '+kwargs['destination']+' ; show ; status ; sleep '+str(kwargs['time'])+' ; status ; report"'
    else:
        command = 'vsh_lc -c "debug platform internal ns elam asic 0 ;' \
                ' trigger init ingress in-select 3 out-select 0 ;' \
                ' set outer ipv4 src_ip '+kwargs['source']+' dst_ip '+kwargs['destination']+' ; show ; status ; sleep '+str(kwargs['time'])+' ; status ; report"'
    #self.log(command)
    port = 22
    #port_2 = 22
    s = paramiko.SSHClient()
    s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print "huh"
    print kwargs['host']
    print kwargs['username']
    print kwargs['password']
    s.connect(kwargs['host'], port, kwargs['username'], kwargs['password'])


    #1 run remote command or script

    (stdin, stdout, stderr) = s.exec_command(command)
    with open('test.txt','w') as myfile:

#look for relavent info and convert to  decimal
        for line in stdout:
            print line
            myfile.write(line)



root = Tk()
a = login(root)
endpoints =find_endpoints(a.ip,a.cookies,a.sip.get(),a.dip.get())
leafs = find_leafs(a.ip,a.cookies)

print endpoints
for endpoint in endpoints:
    if endpoint['role'] == 0:
        for leaf in leafs:
            if leaf['node'] == endpoint['node']:
                print "here"
                elam(host=leaf['oob'],username=a.user.get(), password=a.password.get(),destination=a.dip.get(), source=a.sip.get(), dir='source', time=a.time.get())
    if endpoint['role'] == 1:
        for leaf in leafs:
            print "here"
            if leaf['node'] == endpoint['node']:
                elam(host=leaf['oob'],username=a.user.get(), password=a.password.get(),destination=a.dip.get(), source=a.sip.get(), dir='destination', time = a.time.get())