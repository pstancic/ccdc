import os
import glob
import sys
import re

os.system("systemctl disable firewalld")
os.system("systemctl stop firewalld")
os.system("systemctl enable iptables")
os.system("systemctl start iptables")

if (len(sys.argv) < 2 or os.getuid() != 0):
    print """
    This script will set up interfaces on CentOS Router and MUST be run as root
    Usage: python centos.py teamNumber
    """
    exit()
base_dir = '/etc/sysconfig/network-scripts/'
interfaces = glob.glob(base_dir + 'ifcfg-e*')

teamNum = str(sys.argv[1])

ip = list()
ip[0] = "10.10." + teamNum + ".1"
ip[1] = "192.168.22.1"

if (len(interfaces) == 2):
    for i in range(len(interfaces)):
        string = ''
        f = open(interfaces[i], 'r')
        lines = f.readlines()
        f.close()
        for j in lines:
            string += j
        name = re.match(r'NAME=(\S+)', string)
        device = re.match(r'DEVICE=(\S+)', string)
        UUID = re.match(r'UUID=(\S+)', string)
        config_string = """
        TYPE=Ethernet
        PROXY_METHOD=none
        BOOTPROTO=static
        DEFROUTE=yes
        IPV4_FAILURE_FATAL=no
        IPV6INIT=no
        ONBOOT=yes
        """
        config_string += "\nNAME=" + str(name[1]) + "\nDEVICE=" + str(device[1]) + "\nUUID=" + str(UUID[1])
        config_string += "\nIPADDR=" + ip[i] + "\nNETMASK=255.255.255.0"
        if (i == 0):
            config_string += "\nGATEWAY=10.10." + teamNum + ".2"
        f = open(interfaces[i], 'w')
        f.write(config_string)
        f.close()
else:
    print "Error. There are not 2 interfaces in /etc/sysconfig/network-scripts/"
    exit()

os.system("systemctl restart networking")
os.system("iptables -t nat -F")
os.system("iptables -t nat -X")
os.system("iptables -t nat -A PREROUTING -d 10.10." + teamNum + ".0/24 -j NETMAP --to 192.168.22.0/24")
os.system("iptables -t nat -A POSTROUTING -s 192.168.22.0/24 -j NETMAP --to 10.10." + teamNum + ".0/24")
os.system("iptables-save > /etc/iptables")