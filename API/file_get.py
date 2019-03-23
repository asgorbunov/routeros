import ftplib

devices = [
	{ 'ip': '172.16.16.13',
	'login': 'user',
	'pass': 'user'},
	{ 'ip': '172.16.16.12',
	'login': 'spw',
	'pass': 'spw'}]

filename_pattern = 'backup_{}.backup'

for device in devices:
	print("Connect to {}:".format(device['ip']))
	
	filename = filename_pattern.format(device['ip'])

	with ftplib.FTP(device['ip'], device['login'], device['pass']) as con:
		with open(filename, "wb") as f:
			con.retrbinary('RETR ' + filename, f.write)
			print("    File transfer: done")
