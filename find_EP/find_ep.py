__author__ = 'sheastma'

import sys
from cobra.model.fabric import Inst
from cobra.model.fabric import Topology
from cobra.mit.session import LoginSession
from cobra.mit.access import MoDirectory
from Tkinter import *
import re
import csv


def login(apicUrl, user, password):
    try:
        loginSession = LoginSession(apicUrl,user,password)
        moDir = MoDirectory(loginSession)
        moDir.login()
    except:
        print "the username and/or password you entered is incorrect"
    return moDir

def close_device(Master):
    Master.destroy()

def find_ep(moDir):
    endpoints = []
    eps =moDir.lookupByClass("fvEp")
    count = 0
    for i in eps:
        if str(i.dn).startswith("uni/tn"):
            print i.dn
            temp = {'tn': "",'app':"",'epg':"",'node':"",'port':"",'IP':"",'mac':""}
            count = count+1
            temp['tn'] = (re.findall("tn-(.+)/ap", str(i.dn)))
            temp['app'] = (re.findall("ap-(.+)/epg", str(i.dn)))
            temp['epg'] = (re.findall("epg-(.+)/cep", str(i.dn)))
            try:
                child_TPE = moDir.lookupByClass("fvRsCEpToPathEp", i.dn)
                for j in child_TPE:
                    temp['port'] = (re.findall("pathep-\[(.+)\]\]", str(j.dn)))
                    temp['node'] = (re.findall("paths-(.+)/pa", str(j.dn)))
            except:
                continue
            temp['mac'] = i.mac
            temp['IP'] = i.ip
            endpoints.append(temp)
    return endpoints

def login_gui():
    Master =Tk()
    Master.title("Cisco APIC Login")
    ment = StringVar()
    ment_2 = StringVar()
    ment_3 = StringVar()
    label_1 = Label(Master, text = "ip address").pack()
    mentry = Entry(Master,textvariable = ment ).pack()
    label_2 = Label(Master, text = "username").pack()
    mentry_2 = Entry(Master,textvariable = ment_2 ).pack()
    label_3 = Label(Master, text = "password").pack()
    mentry_3 = Entry(Master,textvariable = ment_3 ).pack()
    frame = Frame(Master)
    frame.pack()
    button = Button(frame,text = "ok", command = lambda: close_device(Master), bg = "red",fg = "blue")
    button.pack()
    Master.mainloop()
    a = ment.get()
    b = ment_2.get()
    c = ment_3.get()
    return a,b,c

def dic_2_excel(ep):
    table = Tk()

    Lb1 = Listbox(table)
    count = 0

    result = open("newfile_3.csv",'wb')


    fieldnames = ['Tenant', 'AP','EPG','Port','Node', 'MAC','IP']
    writer = csv.DictWriter(result, fieldnames=fieldnames, dialect='excel')
    writer.writeheader()
    for i in ep:
        writer.writerow({'Tenant': i["tn"],'AP': i["app"],'EPG': i["epg"],'Port' : i["port"], 'Node': i["node"],'MAC': i["mac"],'IP':i["IP"]})
    result.close

def main():
    a, b, c = login_gui()
    ep = find_ep(login("https://"+a,b,c))
    dic_2_excel(ep)

if __name__ == "__main__":
    try:
	    main()
    except:
        print sys.exc_info()[0]
