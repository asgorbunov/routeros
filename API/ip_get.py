import libapi

devices = [
	{ 'ip': '172.16.16.13',
	'login': 'user',
	'pass': 'user'},
	{ 'ip': '172.16.16.12',
	'login': 'spw',
	'pass': 'spw'}]
    
for device in devices:
	print("Connect to {}:".format(device['ip']))

	#Создание сокета и объекта устройства
	s = libapi.socketOpen(device['ip'])
	dev_api = libapi.ApiRos(s)

	#Авторизация на устройстве
	if not dev_api.login(device['login'], device['pass']):
		break

	#Список команд
	command = ["/ip/address/print"]
	
	#Выполнение команды на устройстве
	dev_api.writeSentence(command)
	
	#Получение результата выполнения команды
	res = libapi.readResponse(dev_api)
	
	#Закрытие сокета
	libapi.socketClose(s)

	#Форматированный вывод результата команды
	print("    Command result:")
	print("        {:^18} {:10}".format('IP', 'Interface'))
	
	for element in res:
		print("        {:18} {:^10}".format(element[2].split('=')[2],
										  element[4].split('=')[2]))
	
	print('')
