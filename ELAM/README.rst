=====================
ELAM Generator (beta)
=====================

This script will look through the APIC database for the two endpoints in question and will find the path that it lies on the fabric and generate a ELAM report on the leaf node(s) that it uses to enter/exit the fabric.

*********
Requires:
*********


Paramiko >= 1.13+ ( >=1.7.5+ if Python2) requests (tested on 2.8.1)

*****************************
Optional:
*****************************

bottle 0.12.9


Supports:

Cisco ACI - Will only find endpoints that aren't learned on the infra vlan and are not learned through a VPC

*************
Instructions:
*************
ELAM capture for ingress and egress of two endpoints entering and leaving the
fabric

optional arguments:
  -h, --help            show this help message and exit
  -i IPADDRESS, --ipaddress IPADDRESS
                        IP address of APIC i.e. 10.122.141.60
  -u USERNAME, --username USERNAME
                        Username for APIC/leaf
  -p PASSWORD, --password PASSWORD
                        Password for APIC/leaf
  -d DESTINATION, --destination DESTINATION
                        Destination endpoint IP address
  -s SOURCE, --source SOURCE
                        Source endpoint IP address
  -t TIME, --time TIME  Time the capture waits before printing the report

Example for running script:

C:\\Users\sheastma\\PycharmProjects\\test> python elam -i "10.122.141.109" -u "admin" -p "password" -d "192.168.1.50" -s "10.199.42.67" -t "5"

**********************
Optional GUI available
**********************

The application can also run as a web based application and will run on TCP port 8082 and the loopback IP address (127.0.0.1 or localhost) of the machine where it is running. it can be excuted by type:

C:\\Users\\sheastma\\PycharmProjects\\test> python elam_bt_server.py

and then going to the following address: http://127.0.0.1:8082/index.html
