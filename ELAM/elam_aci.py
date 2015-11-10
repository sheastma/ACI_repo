#from __future__ import unicode_literals, absolute_import, print_function
import json
import requests
#import urllib3
import paramiko
import re
import sys

"""
        Auto Generated ELAM script for n9k in ACI mode.

        Given a source and destination for your End Point it will
        find which leaf that the end point resides and generate a
        ELAM Capture for the ingress packets coming into the fabric.

        Inputs:

        APIC IP: The IP address of your APIC. **Do not include https**

        APIC Username

        APIC Password

        Source IP: The Source IP for the ELAM Capture

        Destination IP: The Destination IP for the ELAM Capture

        Time: The time the Triggered ELAM will wait before creating a report.
        If no packet is sent during this window no report will be generated.


        For issues with this script, please contact sheastma@cisco.com

"""

def main(A_ip, user_id, user_password, ip_src,ip_dst, time):
        response = ''
        try:
            Mcookies = login(A_ip,user_id,user_password)
        except requests.ConnectionError, e:
            return e
            exit(1)
        except requests.HTTPError, e:
            return e
            exit(1)
        print "here"
        endpoints =find_endpoints(A_ip,Mcookies,ip_src,ip_dst)
        if not endpoints:
            return 'Could not find any Endpoints with IP address '+ip_src+ ' or '+ ip_dst
        leafs = find_leafs(A_ip,Mcookies)
        for endpoint in endpoints:
            if endpoint['role'] == 0:
                for leaf in leafs:
                    if leaf['node'] == endpoint['node']:
                        response = 'ELAM Capture for '+endpoint['ip']+' found on Leaf '+leaf['node']
                        return response
                        response +=elam(host=leaf['oob'],username=user_id, password=user_password,destination=ip_dst, source=ip_dst, dir='source', time=time)
            if endpoint['role'] == 1:
                for leaf in leafs:
                    if leaf['node'] == endpoint['node']:
                        response +='\nELAM Capture for '+endpoint['ip']+' found on Leaf '+leaf['node']+'\n'
                        response +=elam(host=leaf['oob'],username=user_id, password=user_password,destination=ip_dst, source=ip_src, dir='destination', time = time)
        return response



def login( base_url, user, password):
    login_url = 'https://' + base_url + '/api/aaaLogin.json'
    name_pwd = {'aaaUser': {'attributes': {'name': user, 'pwd': password}}}
    json_credentials = json.dumps(name_pwd)
    post_response = requests.post(login_url, data=json_credentials, verify = False)
    post_response.raise_for_status()
    auth = json.loads(post_response.text)
    login_attributes = auth['imdata'][0]['aaaLogin']['attributes']
    auth_token = login_attributes['token']
    # create cookie array from token
    cookies = {}
    cookies['APIC-Cookie'] = auth_token

    return cookies

def find_endpoints(ip, cookies, *args):
    endpoint_url = 'https://'+ ip + '/api/node/class/fvCEp.json'
    paths_url =  'https://'+ ip + '/api/node/class/fvRsCEpToPathEp.json'
    get_response = requests.get(endpoint_url,verify = False, cookies = cookies)
    get_response_2 = requests.get(paths_url,verify = False, cookies = cookies)
    response = json.loads(get_response.text)
    response_2 = json.loads(get_response_2.text)
    count = int(response["totalCount"])
    paths = []
    count_2 = int(response_2["totalCount"])
    if args[0]:
        for i in xrange(0,count,1):
            for j,arg in enumerate(args):
                if (arg ==response['imdata'][i]['fvCEp']['attributes']['ip']):
                    path = {'node':'','ip':arg,'mac':response['imdata'][i]['fvCEp']['attributes']['mac'],'role':j}
                    paths.append(path)

        for i in xrange(0,count_2,1):
            mac = re.findall("cep-(.+)/rsc",response_2['imdata'][i]['fvRsCEpToPathEp']['attributes']['dn'])
            for path in paths:
                if mac[0] == path['mac']:
                    if re.search("paths-(.+)/pathep-\[eth",response_2['imdata'][i]['fvRsCEpToPathEp']['attributes']['tDn']):
                        node =re.findall("paths-(.+)/pathep-\[eth",response_2['imdata'][i]['fvRsCEpToPathEp']['attributes']['tDn'])
                        path['node'] = node[0]
        return paths

def find_leafs(ip, cookies):
    leaf_url = 'https://'+ ip + '/api/node/class/topSystem.json'
    get_response = requests.get(leaf_url,verify = False, cookies = cookies)
    response = json.loads(get_response.text)
    count = int(response["totalCount"])
    leafs = []
    for i in range(0,count,1):
        if response['imdata'][i]['topSystem']['attributes']['role'] == 'leaf':
            temp = {'name':response['imdata'][i]['topSystem']['attributes']['name'],
             'node':response['imdata'][i]['topSystem']['attributes']['id'],
             'oob':response['imdata'][i]['topSystem']['attributes']['oobMgmtAddr']}
            leafs.append(temp)
    return leafs

def elam(**kwargs):

    if kwargs['dir'] == 'source':

        command = 'vsh_lc -c "debug platform internal ns elam asic 0 ;' \
                ' trigger init ingress in-select 3 out-select 0 ;' \
                ' set outer ipv4 src_ip '+kwargs['source']+' dst_ip '+kwargs['destination']+' ; show ; status ; start ; sleep '+str(kwargs['time'])+' ; status ; report"'
    else:
        command = 'vsh_lc -c "debug platform internal ns elam asic 0 ;' \
                ' trigger init ingress in-select 3 out-select 0 ;' \
                ' set outer ipv4 src_ip '+kwargs['destination']+' dst_ip '+kwargs['source']+' ; show ; status ; start ; sleep '+str(kwargs['time'])+' ; status ; report"'
    port = 22
    s = paramiko.SSHClient()
    s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    s.connect(kwargs['host'], port, kwargs['username'], kwargs['password'])
    test ='REPORT\n'
    (stdin, stdout, stderr) = s.exec_command(command)
    for line in stdout:
        if(re.search("Report for Instance 0",line)):
            test+= "**************************REPORT***************************"+"<br>"
        test += line+"<br>"
    return test


if __name__ == "__main__":
   try:
        import argparse
        parser = argparse.ArgumentParser(description='ELAM capture for ingress and egress of two endpoints entering and '
                                                     'leaving the fabric', argument_default=False)
       # parser.add_argument('-l', '--login', help='Use GUI to login', action = 'store_true', default= False,required=False)
        parser.add_argument('-i', '--ipaddress', type = str,help='IP address of APIC i.e. 10.122.141.60', default= False,required=True)
        parser.add_argument('-u', '--username', type = str,help='Username for APIC/leaf',  default= False,required=True)
        parser.add_argument('-p', '--password',type = str, help='Password for APIC/leaf',  default= False, required=True)
        parser.add_argument('-d', '--destination', type = str,help='Destination endpoint IP address',default= False, required=True)
        parser.add_argument('-s', '--source',type = str, help='Source endpoint IP address', default= False, required=True)
        parser.add_argument('-t', '--time', type = str,help='Time the capture waits before printing the report', default= False, required=True)
        args = parser.parse_args()
        print args
        response =main(args.ipaddress,args.username,args.password,args.destination,args.source,args.time)
        f =open('elam.txt','w')
        print response
        f.write(response)

        print '\n'+'\n'+'\n'+'\n'+'\n'+response
        print args.ipaddress+args.username+args.password+args.destination+args.source+args.time
   except IOError, e:
        print e
