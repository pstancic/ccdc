import os
import glob
import sys
import re

if (len(sys.argv) < 2 or len(sys.argv[1]) != 2 or os.getuid() != 0):
    print """
    This script will set up correct packages, interfaces, and iptables on CentOS Router and MUST be run as root
    Usage: python centos.py teamNumber 
    (teamNumber is 2 characters long. i.e. team 1 == 01, team 10 == 10, team 20 == 20)
    """
    exit(1)

os.system("yum install libssh tcpdump wget curl dig iptables iptables-services net-tools bind-utils nano emacs lsof httpd postgresql postgresql-server -y")

os.system("echo 1 > /proc/sys/net/ipv4/ip_forward")
os.system("sysctl -w net.ipv4.ip_forward=1")
os.system("postgresql-setup initdb") # start optimization
os.system("systemctl enable postgresql")
os.system("systemctl start postgresql")
os.system("echo 'SwordAndSt0n3!' > /var/lib/pgsql/root.pass")
os.system("chmod 777 /var/lib/pgsql/root.pass")
os.system("chmod u+s /var/lib/pgsql/root.pass") # end optimization
os.system("systemctl disable firewalld")
os.system("systemctl stop firewalld")
os.system("systemctl enable iptables")
os.system("systemctl start iptables")
os.system("iptables -F")

base_dir = '/etc/sysconfig/network-scripts/'
interfaces = glob.glob(base_dir + 'ifcfg-e*')

teamNum = str(sys.argv[1])

ip = list()
ip.append("10.47.1" + teamNum + ".2")
ip.append("10.57.1" + teamNum + ".1")
ip.append("192.168.220.1")

if (len(interfaces) == 2):
    for i in range(len(interfaces)):
        string = ''
        f = open(interfaces[i], 'r')
        lines = f.readlines()
        f.close()
        for j in lines:
            string += j
        name = re.search(r'NAME=(\S+)', string)
        device = re.search(r'DEVICE=(\S+)', string)
        UUID = re.search(r'UUID=(\S+)', string)
        if (i == 0):
            config_string = "TYPE=Ethernet\nPROXY_METHOD=none\nBOOTPROTO=static\nDEFROUTE=yes\nIPV4_FAILURE_FATAL=no\nIPV6INIT=no\nONBOOT=yes"
            config_string += "\nNAME=" + str(name.group(1)) + "\nDEVICE=" + str(device.group(1)) + "\nUUID=" + str(UUID.group(1))
            config_string += "\nIPADDR0=" + ip[i] + "\nPREFIX0=30"
            config_string += "\nGATEWAY0=10.47.1" + teamNum + ".1"
            config_string += "\nIPADDR1=" + ip[i+1] + "\nPREFIX1=24"
            config_string += "\nDNS1=192.168.220.3" + "\nDNS2=10.0.0.2"
        else:
            config_string = "TYPE=Ethernet\nPROXY_METHOD=none\nBOOTPROTO=static\nDEFROUTE=yes\nIPV4_FAILURE_FATAL=no\nIPV6INIT=no\nONBOOT=yes"
            config_string += "\nNAME=" + str(name.group(1)) + "\nDEVICE=" + str(device.group(1)) + "\nUUID=" + str(UUID.group(1))
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
os.system("iptables -t nat -A PREROUTING -d 10.57.1" + teamNum + ".0/24 -j NETMAP --to 192.168.220.0/24")
os.system("iptables -t nat -A POSTROUTING -s 192.168.220.0/24 -j NETMAP --to 10.57.1" + teamNum + ".0/24")
os.system("iptables-save > /etc/iptables")
