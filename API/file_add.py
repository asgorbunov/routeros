import ftplib

devices = [
	{ 'ip': '172.16.16.13',
	'login': 'user',
	'pass': 'user'},
	{ 'ip': '172.16.16.12',
	'login': 'spw',
	'pass': 'spw'}]

filename = 'script_spw'

for device in devices:
	print("Connect to {}:".format(device['ip']))
	
	with ftplib.FTP(device['ip'], device['login'], device['pass']) as con:
		with open(filename, "rb") as f:
			send_file = con.storbinary("STOR " + filename, f)
			print("    File transfer: done")
