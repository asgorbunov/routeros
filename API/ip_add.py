import libapi

devices = [
	{ 'ip': '172.16.16.13',
	'login': 'user',
	'pass': 'user'},
	{ 'ip': '172.16.16.12',
	'login': 'spw',
	'pass': 'spw'}]

new_network = '10.52.52.{}/32'
new_interface = 'br_ospf'

for device in devices:
	print("Connect to {}:".format(device['ip']))

	#Создание сокета и объекта устройства
	s = libapi.socketOpen(device['ip'])
	dev_api = libapi.ApiRos(s)

	#Авторизация на устройстве
	if not dev_api.login(device['login'], device['pass']):
		break

	#Команда для добавление bridge-интерфейса
	command = ["/interface/bridge/add", "=name={}".format(new_interface)]
	
	#Выполнение команды на устройстве
	dev_api.writeSentence(command)

	#Получение результата выполнения команды
	res = libapi.readResponse(dev_api)
	
	#Команда для добавления IP-адреса на bridge-интерфейс
	command = ["/ip/address/add",
		"=address={}".format(new_network.format(device['ip'].split('.')[3])),
		"=interface={}".format(new_interface)]
		
	#Выполнение команды на устройстве
	dev_api.writeSentence(command)
	
	#Получение результата выполнения команды
	res = libapi.readResponse(dev_api)
	
	#Закрытие сокета
	libapi.socketClose(s)
	
