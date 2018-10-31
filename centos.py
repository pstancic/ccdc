import os
import glob
import sys
import re

if (len(sys.argv) < 2 or os.getuid() != 0):
    print """
    This script will set up interfaces on CentOS Router and MUST be run as root
    Usage: python centos.py teamNumber
    """
    exit()

os.system("yum install libssh tcpdump wget curl htop iptables iptables-services net-tools bind-utils nano lsof -y")

os.system("echo 1 > /proc/sys/net/ipv4/ip_forward")
os.system("sysctl -w net.ipv4.ip_forward=1")
os.system("systemctl disable firewalld")
os.system("systemctl stop firewalld")
os.system("systemctl enable iptables")
os.system("systemctl start iptables")
os.system("iptables -F")

base_dir = '/etc/sysconfig/network-scripts/'
interfaces = glob.glob(base_dir + 'ifcfg-e*')

teamNum = str(sys.argv[1])

ip = list()
ip.append("10.42.1" + teamNum + ".2")
ip.append("10.52.1" + teamNum + ".1")
ip.append("192.168.220.1")

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
        if (i == 0):
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
            config_string += "\nIPADDR0=" + ip[i] + "\nPREFIX0=30"
            config_string += "\nGATEWAY=10.47.1" + teamNum + ".1"
            config_string += "\nIPADDR1=" + ip[i+1] + "\nPREFIX1=24"
        else:
            config_string = """
            TYPE=Ethernet
            PROXY_METHOD=none
            BOOTPROTO=static
            DEFROUTE=yes
            IPV4_FAILURE_FATAL=no
            IPV6INIT=no
            ONBOOT=yes
            NAME=
            """
            config_string += str(name[1]) + "\nDEVICE=" + str(device[1]) + "\nUUID=" + str(UUID[1])
            config_string += "\nIPADDR=" + ip[i+1] + "\nNETMASK=255.255.255.0"
        f = open(interfaces[i], 'w')
        f.write(config_string)
        f.close()
else:
    print "Error. There are not 2 interfaces in /etc/sysconfig/network-scripts/"
    exit()

os.system("systemctl restart network")
os.system("iptables -t nat -F")
os.system("iptables -t nat -X")
os.system("iptables -t nat -A PREROUTING -d 10.52.1" + teamNum + ".0/24 -j NETMAP --to 192.168.220.0/24")
os.system("iptables -t nat -A POSTROUTING -s 192.168.220.0/24 -j NETMAP --to 10.52.1" + teamNum + ".0/24")
os.system("iptables-save > /etc/iptables")
