#!/usr/bin/env
__author__ = 'sheastma'
__version__ = '1.0.1'

try:
    import paramiko
    from paramikoe import SSHClientInteraction

except ImportError:
    print 'This script requires Paramikoe a third party module in python'
import sys
import argparse
import threading

global leafs
leafs = []


def get_creds():
    parser = argparse.ArgumentParser('add credential file')
    parser.add_argument('filename')
    args = parser.parse_args()
    with open(args.filename) as f:
        scp_url = f.readline()
        scp_pwd = f.readline()
        node_ip = f.readline()
        fab_username = f.readline()
        fab_pwd = f.readline()
    scp_url = scp_url.split(',')[1]
    scp_pwd = scp_pwd.split(',')[1]
    fab_username = fab_username.split(',')[1]
    fab_pwd = fab_pwd.split(',')[1]
    node_ip = node_ip.split(',')[1:]

    return scp_url, scp_pwd, fab_username, fab_pwd, node_ip


def workon(host, username, password, scp_url, scp_pass):
    cmd1 = 'sshpass -p ' + scp_pass.rstrip() + ' scp -v -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ' \
           + scp_url.rstrip() + ' /bootflash/'
    cmd2 = 'setup-bootvars.sh ' + scp_url[scp_url.rfind("/") + 1:].rstrip() + ' '
    cmd3 = 'setup-clean-config.sh ; vsh -c "reloadg"'
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    host = host.rstrip()
    username = username.rstrip()
    password = password.rstrip()
    print '******** HOST IP ' + host + " ********" + '\n'

    try:
        ssh.connect(hostname=host, username=username, password=password)
        interact = SSHClientInteraction(ssh, timeout=50, display=True)
        try:
            interact.send(cmd1)
            interact.expect('.*Exit status 0.*', timeout=20)
            interact.current_output_clean
        except:
            print "\n" + host + " image did not download correctly. Please check scp information and try again."
            ssh.close()
            return

        try:
            interact.send(cmd2)
            interact.expect('.*Done.*')
            interact.current_output_clean
        except:
            print "\n" + host + " A issue arose while trying to set the boot variables. Please verify the switch is" \
                                " supported under this script"
            ssh.close()
            return
        try:
            interact.send(cmd3)
            interact.expect('Done')
            interact.current_output_clean
        except:
            print "\n" + host + " Something went wrong while trying to reload the switch. " \
                                "Please check the switch or reload manually"
            ssh.close()
            return

    except paramiko.AuthenticationException:
        print host + " is unable to authenticate with the credentials provided. Please double check them and try again."
        ssh.close()

    print '*' * 40
    print '*' * 40

def main():
    scp_url, scp_pwd, fab_username, fab_pwd, node_ip = get_creds()
    threads = []
    print len(node_ip)
    for ip in node_ip:
        # bug fix - workaround
        ip = ip.rstrip()
        print 'IP ' + ip + ' is being added into the thread'
        t = threading.Thread(target=workon, args=(ip, fab_username, fab_pwd, scp_url, scp_pwd, ))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()


if __name__ == "__main__":
    try:
        main()
    except:
        print sys.exc_info()
