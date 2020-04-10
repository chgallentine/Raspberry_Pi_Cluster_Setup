# -*- coding: utf-8 -*-
# @Author: charliegallentine
# @Date:   2020-04-10 12:03:19
# @Last Modified by:   charliegallentine
# @Last Modified time: 2020-04-10 16:15:30

import os
import re
import shutil
import sys

HOSTNAME_DIRECTORY = './hostnames_tmp'
MACHINEFILE = './machinefile'

COMPUTER_LIST = []

# Get information about master node
ip_master = os.popen('hostname -I').read()[:-2]
hostname_master = os.popen('hostname').read()[:-1]

# Finds all valid ip addresses 
regex_ip = re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b")

# Regex to discover if node needs to be renamed
regex_hostname = re.compile(r"node\w{4}")

# Will be used to find other node's ip addresses
cmd_nmap = 'nmap -sn ' + ip_master[:-1] + '*';
# Use nmap command to find all ip addresses in local network
nmap_res = os.popen(cmd_nmap).read()

# Find all valid ip addresses
ip_addrs = re.findall(regex_ip, nmap_res)

# Filter found ip addresses by "not master" and not local connection and same range
ip_addrs = [x for x in ip_addrs if x[:-1] == ip_master[:-1] and x[-1] != '1' and x != ip_master]

# Temporary file structure to retrieve all hostnames
# 	Can be used to verify hosts as valid and add others
if os.path.exists(HOSTNAME_DIRECTORY) and os.path.isdir(HOSTNAME_DIRECTORY):
        shutil.rmtree(HOSTNAME_DIRECTORY)
os.mkdir(HOSTNAME_DIRECTORY)

# Machinefile used to collect hosts while running MPI program
if os.path.exists(MACHINEFILE):
	os.remove(MACHINEFILE)
fmachine = open(MACHINEFILE,'a')

# Info about master node at top of file
fmachine.write(ip_master + " # " + hostname_master + " MASTER\n")
COMPUTER_LIST.append([ip_master,hostname_master])

# For each discovered ip address, ad to machine file
for ip in ip_addrs:
	fname = os.path.join(HOSTNAME_DIRECTORY, ip.replace('.','_') + "_hostname")

	cmd_scp = "scp " + ip + ":/etc/hostname " + fname
	cmd_cat = "cat " + fname

	os.popen(cmd_scp)
	hostname = os.popen(cmd_cat).read()[:-1]

	machinefile_line = ip + " # " + hostname + "\n"

	fmachine.write(machinefile_line)
	COMPUTER_LIST.append([ip,hostname])


for node in COMPUTER_LIST:
	# Copy master public key to remote .ssh directory
	print("From master to %s" % (node[1]))
	cmd_scp = "scp " + "~/.ssh/id_rsa.pub " + node[0] + ":~/.ssh/" + hostname_master
	os.popen(cmd_scp)

	# Copy remote rsa public key into master .ssh directory
	print("From %s to master" % (node[1]))
	cmd_scp =  "scp  " + node[0] + ":~/.ssh/id_rsa.pub " + "~/.ssh/" + node[1]
	os.popen(cmd_scp)

if os.path.exists("/home/pi/.ssh/authorized_keys"):
	os.remove("/home/pi/.ssh/authorized_keys")
open("/home/pi/.ssh/authorized_keys",'a').close()

for node in os.listdir("/home/pi/.ssh"):
	if re.match(regex_hostname, node):
		path = os.path.join("/home/pi/.ssh", node)

		cmd_cat = "cat " + path + " >> /home/pi/.ssh/authorized_keys" 
		os.popen(cmd_cat)

for node in COMPUTER_LIST:
	cmd_scp = "scp /home/pi/.ssh/authorized_keys " + node[0] + ":/home/pi/.ssh/"
	os.popen(cmd_scp)
	cmd_scp = "scp /home/pi/.ssh/authorized_keys " + node[0] + ":/home/pi/.ssh/known_hosts"
	os.popen(cmd_scp)


# Cleanup
fmachine.close()
shutil.rmtree(HOSTNAME_DIRECTORY)















