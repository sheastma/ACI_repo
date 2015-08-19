Auto Manual Upgrade
===================

This is a simple script to perform a manual upgrade on multiple 
switches in your ACI (Application Centric Infrastructure) fabric.

<br>
##### Requires: #####
Paramiko >= 1.13+ ( >=1.7.5+ if Python2) 
paramikoe 
creds.csv - needs to be populated with fabric information
     
<br>  
##### Supports: #####
Cisco ACI - Up to 12 switches at a time (Leafs and Spines)
<br>   

#### Instructions: ####

Populate the creds.csv file and upgrade the script with the 
correct path to the creds.csv file.


Example for running script:

prompt# auto_upgrade.py creds.csv