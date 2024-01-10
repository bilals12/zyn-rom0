import subprocess
from netaddr import IPNetwork

# define range of IP addresses to iterate over
ip_range = '41.108.48.1/24'

# iterate over each IP in the range
for ip in IPNetwork(ip_range):
	# execute script.py
	command = ["python", "script.py", str(ip)]

	# execute command using subprocess
	subprocess.run(command)