#Global variables
conf_file = ""
log_file = ""
config_data={'appid':"",'seckey':"",'users_file':"",'routers_file':'','default_router':{'name':"",'file':""},'listening_mode':""}
users =  []
routers = []
current_status_router = ""

#Imports

import thread
import logging
import latch
import os
import datetime
import time
import select
import sys
import os

from time import sleep
from texttable import Texttable
from threading import Timer

import lockifi_modules.users_csv
import lockifi_modules.routers_csv
import lockifi_modules.configuration_module

#Operative system imports
if os.name == 'nt':	# Windows
    import msvcrt
    conf_file = "conf\\conf.cfg"
    path_data = "data\\"
    path_scripts = "routers_scripts\\"
    log_file = "log\\lockifi.log"
else:	# Posix (Linux, OS X)
	conf_file = "conf/conf.cfg"
	path_data = "data/"
	path_scripts = "routers_scripts/"
	log_file = "log/lockifi.log"


#Main functions
def pre_main():
	global users
	global routers
	global log_file
	global conf_file
	global config_data
	
	logging.basicConfig(format='%(asctime)s %(message)s',filename=log_file,level=logging.DEBUG)
	config_data = lockifi_modules.configuration_module.import_configuration(conf_file)
	if config_data==-1:
		print "\n-->A error has been occurred with configuration file\n"
		return 1
	users = lockifi_modules.users_csv.read_users(path_data + config_data['users_file'])
	if users==-1:
		print "\n-->An error has occurred with users file\n"
		return 1
	routers = lockifi_modules.routers_csv.read_routers(path_data + config_data['routers_file'])
	if routers==-1:
		print "\n-->An error has occurred with routers file\n"
		return 1
	try:
		if len(users)>0:
			users_refresh_status();
		len(routers)
	except TypeError:
		print "-->Problem with router or user file."
		return 1
	else:
		return 0
def main():

	while True:
		main_menu()
	return 0

#Support functions
def wait():
	raw_input("Press Enter to continue...")
	return 0
def validate_input(number,min_limit,min_include,max_limit,max_include):
	try:
		number = int(number)
		if min_include==1:
			if number<min_limit:
				return "\nRange format failure: Invalid format\n"
		else:
			if number<=min_limit:
				return "\nRange format failure: Invalid format\n"
		if max_include==1:
			if number>max_limit:
				return "\nRange format failure: Invalid format\n"
		else:
			if number>=max_limit:
				return "\nRange format failure: Invalid format\n"
	except ValueError:
		return "\nInput format failure: Invalid format\n"
	return 0	
def clear():
# Windows
	if os.name == 'nt':
	    os.system('cls') 
	# Posix (Linux, OS X)
	else:
		os.system('clear') 
#Main menu
def main_menu():

	options = {1:users_menu, 2:routers_menu, 3:lockifi_listen_start,4:latch_menu,5:lockifi_conf_menu,6:log_show}
	
	option_selected=0
	while option_selected==0:
		clear()
		print "Lockifi beta - Plugin Latch \n"
		print "Menu: \n"
		print "\t1. Show/edit users"
		print "\t2. Show/edit routers"
		print "\t3. Start listen"
		print "\t4. Config Latch"
		print "\t5. Config Lockifi"
		print "\t6. Show log"
		print "\t7. Exit"
		option = raw_input("Option: ")
		if validate_input(option,1,1,len(options)+1,1)==0:
			option_selected = option
	option = int(option)	
	if option==7:
		clear()
		print "Lockifi beta - Plugin Latch \n"
		print "Thank for use lockifi!"
		exit(0)
	else:	
		ret = options[option]()
		if ret!=0:
			print "Problem running function: ",str(option)
		return ret

#Users functions
def users_menu():
	options = {1:users_show, 2:users_add, 3:users_edit,4:users_delete} #salir provisional
	
	option_selected=0
	while option_selected==0:
		clear()
		print "Lockifi beta - Plugin Latch \n"
		print "Users>options: \n"
		print "\t1. Show paired users"
		print "\t2. Add user"
		print "\t3. Edit user"
		print "\t4. Delete user"
		print "\t5. Back"
		option = raw_input("Option: ")
		if validate_input(option,1,1,len(options)+1,1)==0:
			option_selected = option
	option = int(option)
	if option==1:
		users_show() #Exec with post wait
		wait()
	elif option==5:
		return 0
	else:
		ret = options[option]()

		if ret!=0:
			logging.error("Problem running option "+ str(option) + " of menu")
		return ret
def users_show():
	clear()
	print "Lockifi beta - Plugin Latch \n"
	if len(users) <= 0:
		print "\n-->Dont exist users registered on system.\n"
		return 1
	else:
		print "\nReloading...\n"
		if users_refresh_status()==-1:
			print "\n-->Impossible reload the users\n"
			return 1
		else:
			t = Texttable()
			t.header(['ID','Name','AccountId','Status'])
			i=1
			for user in users:
				t.add_row([i,user['name'],user['accountId'],user['status']])
				i=i+1
			clear()
			print "Lockifi beta - Plugin Latch \n"
			print "\nUSERS: \n"+t.draw()+"\n"
			return 0
def users_add():
	user_name=""
	error=""
	while user_name=="":
		clear()
		print "Lockifi beta - Plugin Latch \n"
		print "Users>Add user: \n"
		print error
		user_name = raw_input("Enter a username[enter 0 to cancel]: ")
		if user_name=="0":
			print "\n-->Operation cancelled\n"
			return 0
		elif user_name=="":
			error = "\n-->You must enter a name for user\n"
		elif users_exist(user_name)==1:
			error = "\n-->The username is already register in Lockifi\n"
			user_name=""
			
	accountId = latch_pair()
	if(accountId==-1):
		print "\n-->A problem has occurred in the communication with the Latch server\n"
		wait()
		return 1
	else:
		users.append({"name": user_name, "accountId": accountId, "status": "unknow"})
		lockifi_modules.users_csv.save_users(path_data + config_data['users_file'],users)
		print "\n-->User added\n"
		wait()
		return 0
def users_edit():
	if len(users) > 0:
		user_selected=-1
		error = ""
		while user_selected==-1:
			users_show()
			print error
			input_number = raw_input("Enter ID of user that you wish edit[enter 0 to cancel]: ")
			validate_response = validate_input(input_number,0,1,len(users),1)
			if validate_response!=0:
				error = validate_response
			else:
				user_selected = int(input_number)
				if user_selected==0:
					print "\n-->Operation cancelled\n"
					wait()
					return 0
				elif user_selected=="":
					error =  "You must enter ID of a user"
					user_selected=-1
				else:
					new_name=-1
					error = ""
					while True:
						users_show()
						print error
						new_name = raw_input("Enter the new name for the user with name '"+ users[user_selected-1]['name'] +"' (press enter to not change it): ")
						if users_exist(new_name)==1:
							error = "\n-->The username is already register in Lockifi\n"
							new_name=-1
						elif new_name!="":
							users[user_selected-1]['name'] = new_name
							lockifi_modules.users_csv.save_users(path_data + config_data['users_file'],users)
							print "\n-->User edited!\n"
							wait()
							return 0
						else:
							return 1
	return 0
def users_delete():
	if len(users) > 0:
		user_selected=-1
		error = ""
		while user_selected==-1:
			users_show()
			print error
			input_number = raw_input("Enter ID of user that you wish delete[enter 0 to cancel]: ")
			validate_response = validate_input(input_number,0,1,len(users),1)
			if validate_response!=0:
				error = validate_response
			else:
				user_selected = int(input_number)
				if user_selected==0:
					print "\n-->Operation cancelled\n"
					wait()
					return 0
				elif user_selected=="":
					error = "You must enter ID of a user"
					user_selected=-1
				else:
					if latch_unpair(users[user_selected-1]['accountId'])==0:
						users.remove(users[user_selected-1])
						lockifi_modules.users_csv.save_users(path_data + config_data['users_file'],users)
						print "\n-->User deleted!\n"
						wait()
						return 0
					else:
						print "\n-->The system cant delete the user!\n"
						wait()
						return 1
	return 0
def users_refresh_status():
	for user in users:
		status = latch_status(user['accountId'])
		if status == -1:
			return -1
		user['status'] = status
	return 0
def users_exist(username):
	for user in users:
		if username==user['name']:
			return 1
	return 0
#Routers functions
def routers_menu():
	options = {1:routers_show, 2:routers_add, 3:routers_edit,4:routers_delete}
	
	option_selected=0
	while option_selected==0:
		clear()
		print "Lockifi beta - Plugin Latch \n"
		print "Routers>options: \n"
		print "\t1. Show routers"
		print "\t2. Add router"
		print "\t3. Edit router"
		print "\t4. Delete router"
		print "\t5. Cancel"
		option = raw_input("Option: ")
		if validate_input(option,1,1,len(options)+1,1)==0:
			option_selected = option
	option = int(option)
	if option==1:
		routers_show() #Exec with post wait
		wait()
	elif option==5:
		return 0
	else:
		ret = options[option]()

		if ret!=0:
			logging.error("Problem running option "+ str(option) + "of menu")
		return ret	
def routers_show():
	
	clear()
	print "Lockifi beta - Plugin Latch \n"
	if len(routers) <= 0:
		print "Dont exist routers register in system."
	else:
		t = Texttable()
		t.header(['ID','Selected','Name','file'])
		i=1
		for router in routers:
			default_router=""
			if default_router=="" and router['file']==config_data['default_router']['file']:
				default_router="*default*"
			t.add_row([str(i),default_router,router['name'],router['file']])
			i=i+1
		print "\nROUTERS: \n"+t.draw()+"\n"
	return 0	
def routers_add():
	router_name=""
	error = ""
	while router_name=="":
		clear()
		print "Lockifi beta - Plugin Latch \n"
		print "Routers>Add router: \n"
		print error
		router_name = raw_input("Enter a name for router[enter 0 to cancel]: ")
		if router_name=="0":
			print "\n-->Operation cancelled\n"
			wait()
			return 0
		elif router_name=="":
			error = "\n-->You must enter a name for router\n"
		elif routers_exist(router_name)==1:
			error = "\n-->The router name is already register in Lockifi\n"
			router_name=""	
			
	router_file=""
	while router_file=="":
		router_file = raw_input("Enter the name of the file configuration of router(inlcude the extension.py)[enter 0 to cancel]: ")
		if router_file=="0":
			print "\n-->Operation cancelled\n"
			return 0
		elif router_file=="":
			print "\n-->You must enter the filename of the router\n"
	if config_data['default_router']['name']!="":
		default = raw_input("Do you want do default this router?(y/n)")
		if default=='y' or default=='Y':
			config_data['default_router']['name'] = router_name
			config_data['default_router']['file'] = router_file
			lockifi_modules.configuration_module.save_configuration(conf_file,"Router","default_router_name",router_name)
			lockifi_modules.configuration_module.save_configuration(conf_file,"Router","default_router_file",router_file)
	else:
		lockifi_modules.configuration_module.save_configuration(conf_file,"Router","router_default_name",router_name)
		lockifi_modules.configuration_module.save_configuration(conf_file,"Router","router_default_file",router_file)
	routers.append({"name": router_name, "file": router_file})
	lockifi_modules.routers_csv.save_routers(path_data + config_data['routers_file'],routers)
	print "\n-->Router added\n"
	wait()
	return 0
def routers_edit():
	if len(routers) > 0:
		router_selected=-1
		error = ""
		while router_selected==-1:
			routers_show()
			print error
			input_number = raw_input("Enter ID of router that you wish edit[enter 0 to cancel]: ")
			validate_response = validate_input(input_number,0,1,len(routers),1)
			if validate_response==0:
				input_number = int(input_number)
				if input_number==0:
					print "\n-->Operation cancelled\n"
					wait()
					return 0
				elif input_number=="":
					error = "You must enter ID of a router"
				else:	
					router_selected = input_number
					
					new_name=-1
					error=""
					while new_name==-1:
						routers_show()
						print error
						new_name = raw_input("Enter the new name for the router with name '"+ routers[router_selected-1]['name'] +"' (press enter to not change it): ")
						if new_name!= "" and routers_exist(new_name)==1:
							error = "\n-->The router is already register in Lockifi\n"
							new_name=-1
						
					if new_name!="":
						routers[router_selected-1]['name'] = new_name
					new_file = raw_input("Enter the new filename for the router with filename '"+ routers[router_selected-1]['file'] +"' (press enter to not change it): ")
					if new_file!="":
						routers[router_selected-1]['file'] = new_file
					default = raw_input("Do you want do default this router?(y/n)")
					if default=='y' or default=='Y':
						config_data['default_router']['name'] = routers[router_selected-1]['name']
						config_data['default_router']['file'] = routers[router_selected-1]['file']
						lockifi_modules.configuration_module.save_configuration(conf_file,"Router","default_router_name",routers[router_selected-1]['name'])
						lockifi_modules.configuration_module.save_configuration(conf_file,"Router","default_router_file",routers[router_selected-1]['file'])
					if lockifi_modules.routers_csv.save_routers(path_data + config_data['routers_file'],routers)!=0:
						print "\n-->Router was not modifieded!\n"
						return 1
					else:
						routers_show()
						print "\n-->Router modifieded!\n"
						wait()
						return 0
			else:
				error = validate_response
def routers_delete():
	if len(routers) > 0:
		router_selected=-1
		error = ""
		while router_selected==-1:
			routers_show()
			print error
			input_number = raw_input("Enter ID of router that you wish delete[enter 0 to cancel]: ")
			validate_response = validate_input(input_number,0,1,len(routers),1)
			if validate_response!=0:
				error = validate_response
			else:
				router_selected = int(input_number)
				if router_selected==0:
					print "\n-->Operation cancelled\n"
					wait()
					return 0
				elif router_selected=="":
					error =  "You must enter ID of a router"
					router_selected=-1
				else:
					if routers[router_selected-1]['name']==config_data['default_router']['name']:
						config_data['default_router']['name'] = ""
						config_data['default_router']['file'] = ""
						lockifi_modules.configuration_module.save_configuration(conf_file,"Router","router_default_name","")
						lockifi_modules.configuration_module.save_configuration(conf_file,"Router","router_default_file","")
						
					routers.remove(routers[router_selected-1])
					lockifi_modules.routers_csv.save_routers(path_data + config_data['routers_file'],routers)
					print "\n-->Router deleted!\n"
					wait()
					return 0
def routers_exist(name):
	for router in routers:
		if name==router['name']:
			return 1
	return 0
	
#Config Latch functions
def latch_menu():
	option_selected=0
	while option_selected==0:
		clear()
		print "Lockifi beta - Plugin Latch \n"
		print "Latch>options: \n"
		print "\t1. Show Latch configuration"
		print "\t2. Edit Latch configuration"
		print "\t3. Back"
		option = raw_input("Option: ")
		if validate_input(option,1,1,3+1,1)==0:
			option_selected = int(option)
			if option_selected==0:
				ret = 0
			elif option_selected==1:
				ret = latch_conf_show();
				wait()
			elif option_selected==2:
				ret = latch_conf_edit()
			elif option_selected==3:
				ret = 0
	if ret!=0:
		logging.error("Problem running option "+ str(option) + " of menu")
	return ret
def latch_conf_show():
	appid = config_data['appid']
	seckey = config_data['seckey']
	if appid=="":
		appid="<empty>"
	if seckey=="":
		seckey="<empty>"
	clear()
	print "Lockifi beta - Plugin Latch \n"
	print "Latch configuration>: \n"
	print "\tAppID: "+ appid
	print "\tSecretKey: "+ seckey+"\n"
	return 0
def latch_conf_edit():
	latch_conf_show()
	
	new_appid = raw_input("Enter the new AppId (press enter to not change it): ")
	if new_appid!="":
		config_data['appid'] = new_appid
		if lockifi_modules.configuration_module.save_configuration(conf_file,"Latch","appid",new_appid)!=0:
				print "\nThe system cant modify the Latch config\n"
				wait()
				return 1
				
	new_seckey = raw_input("Enter the new SecretKey (press enter to not change it): ")
	if new_seckey!="":
		config_data['seckey'] = new_seckey
		if lockifi_modules.configuration_module.save_configuration(conf_file,"Latch","seckey",new_seckey)!=0:
				print "\nThe system cant modify the Latch configuration\n"
				wait()
				return 1
				
	latch_conf_show()
	print "\n-->Latch configuration modifieded\n"		
	wait()
	return 0
def latch_pair():
	api = latch.Latch(config_data['appid'],config_data['seckey'])
	pair_code = raw_input("Enter pairing code: ")
	response = api.pair(pair_code)
	responseData = response.get_data()
	responseError = response.get_error()
	if responseError != "" or responseData =="":
		logging.error("[latch_pair()] Error of paired:" + str(responseError))
		return -1
	else:
		try:
			accountId = responseData.get('accountId')
		except (TypeError, ValueError, AttributeError) as err:
			logging.error("[latch_pair()] Error resolving JSON:" + str(err))
			return -1
		else:
			return accountId
def latch_unpair(accountId):
	api = latch.Latch(config_data['appid'],config_data['seckey'])
	
	response = api.unpair(accountId)
	responseData = response.get_data()
	responseError = response.get_error()
	
	if responseError != "" :
		logging.error("[latch_pair()] Error of unpaired:" + str(responseError))
		return 1
	else:
		return 0
def latch_status(accountId):
	api = latch.Latch(config_data['appid'],config_data['seckey'])
	response = api.status(accountId)
	responseData = response.get_data()
	responseError = response.get_error()
	if responseError != "" or responseData =="":
		logging.error("[latch_status()] Error of reload status:" + str(responseError))
		return -1
	else:
		try:
			status = responseData['operations'][config_data['appid']]['status']
		except:
			status = "unknow"
		return status	

#Config Lockifi functions
def lockifi_conf_menu():
	options = {1:lockifi_conf_show, 2:lockifi_conf_edit}
	
	option_selected=0
	error = ""
	while option_selected==0:
		clear()
		print "Lockifi beta - Plugin Latch \n"
		print "Lockifi>options: \n"
		print "\t1. Show Lockifi configuration"
		print "\t2. Edit Lockifi configuration"
		print "\t3. Back"
		print error
		option = raw_input("Option: ")
		validate_response = validate_input(option,1,1,len(options)+1,1)
		if validate_response!=0:
			error = validate_response
		else:
		
			ret = 0
			option_selected = int(option)
			if option_selected==0:
				ret = 0
			if option_selected==1:
				ret = lockifi_conf_show()
				wait()
			elif option_selected==2:
				lockifi_conf_edit()
				ret=0
			elif option_selected==3:
				ret=0
			else:
				ret=1
	if ret!=0:
		logging.error("Problem running option "+ str(option) + " of menu")
	return ret	
def lockifi_conf_show():
	clear()
	print "Lockifi beta - Plugin Latch \n"	
	print "Lockifi configuration>: \n"
	print "\tListening mode: "+ config_data['listening_mode']+"\n"
	return 0
def lockifi_conf_edit():
	modes = {1:"all_open",2:"changes"}
	mode_selected=-1
	error=""
	while mode_selected==-1:
		lockifi_conf_show()
		print error
		new_mode = raw_input("Enter the new mode [1:all_open/2:changes] (press 0 to cancel): ")
		validate_response = validate_input(new_mode,0,1,len(modes),1)
		if validate_response!=0:
			error = validate_response
		else:
			mode_selected=int(new_mode)
			if mode_selected==0:
				print "\n-->Operation cancelled\n"
				wait()
				return 0
			config_data['listening_mode'] = modes[mode_selected]
			if lockifi_modules.configuration_module.save_configuration(conf_file,"Lockifi","listening_mode",modes[mode_selected])!=0:
				print "\n-->The system cant modify the Lickifi configuration\n"
				wait()
				return 1
	lockifi_conf_show()
	print "\n-->Lickifi configuration modifieded\n"	
	wait()
	return 0
				
#Listen functions	
def lockifi_listen_start():
	global current_status_router
	global record_str
	
	if len(users)>0 and len(routers)>0:
		listening=1
		print "Lockifi beta - Plugin Latch \n"
		print "Listening>: \n"
		if not os.path.exists(path_scripts+ config_data['default_router']['file'] ):
			print "\n-->The system is not be able to find the router script file\n"
			wait()
			return 1
		if(users_show() == 1):
			print "\n-->The system cant listen because has a problem to reload the status of the users\n"
			wait()
			return 1
		status = {1:"on",2:"off"}

		while current_status_router=="":
			new_mode = raw_input("Enter the current status of wifi [1:on/2:off](press 0 to cancel listen): ")
			if validate_input(new_mode,0,1,len(status),1)==0:
				if int(new_mode) == 0:
					print '\nListen canceled\n'
					wait()
					return 1
				current_status_router=status[int(new_mode)]
		users_show()
		logging.info("Listen start")
		print "Wifi: "+current_status_router
		print "Listening...(Press enter to stop): "
		list = []
		thread.start_new_thread(input_thread, (list,))
		record_str = ""
		while not list:
			if config_data['listening_mode']=="changes":
				lockifi_listen_mode_changes()
			elif config_data['listening_mode']=="all_open":
				lockifi_listen_mode_all_open()
			else:
				print "\nProblem with the listening_mode on Lockifi configuration\n"
				wait()
				return 1
			
		current_status_router=""
		logging.info("Listen finish");
		print '\nListen finish!\n'
		wait()
		return 0
	else:
		print "\n-->There aren't users or routers registred on the system\n"
		wait()
		return 0
def input_thread(list):
    raw_input()
    list.append(None)
def lockifi_listen_mode_changes():
	global record_str
	global current_status_router
	if len(record_str)>2000:
		record_str=""
		
	for user in users:
		current_status_here = user['status']
		current_status_latch = latch_status(user['accountId'])
		
		if current_status_latch!=current_status_here:
			user['status']=current_status_latch
			if current_status_latch!=current_status_router:
				current_status_router = current_status_latch
				users_show()
				print record_str
				
				if current_status_latch=="on":
					logging.info(user['name']+"Change wifi status to on");
					record_str = record_str + lockifi_enable_router()

				else:
					logging.info(user['name']+ " change wifi status to off");
					record_str = record_str + lockifi_disable_router()

				print "Wifi: "+current_status_router
				print "Listening...(Press enter to stop): "
	return 0	
def lockifi_listen_mode_all_open():
	global record_str
	global current_status_router
	
	if len(record_str)>2000:
		record_str=""
	global_status = "on"
	for user in users:
		current_status_latch = latch_status(user['accountId'])
		if current_status_latch=="off":global_status = "off"
		
	if global_status!=current_status_router:
		current_status_router = global_status
		users_show()
		print record_str
		if global_status=="on":
			record_str = record_str + lockifi_enable_router()
		else:
			record_str = record_str + lockifi_disable_router()
		
		print "Wifi: "+current_status_router
		print "Listening...(Press enter to stop): "

def lockifi_enable_router():
	toret = ""
	time_start = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	print "["+ str(time_start) +"] -> Enabling wifi (impossible stop process)\n"
	toret = toret + "["+ str(time_start) +"] -> Enabling wifi (impossible stop process)\n"
	os.system("python " + path_scripts + config_data['default_router']['file'] +" 1")
	time.sleep(10)
	print "\tWifi enabled\n"
	toret = toret +  "\tWifi enabled\n"
	return str(toret)
def lockifi_disable_router():
	toret=""
	time_start = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	print "["+ str(time_start) +"] -> Disabling wifi (impossible stop process)\n"
	toret = toret + "["+ str(time_start) +"] -> Disabling wifi (impossible stop process)\n"
	os.system("python " + path_scripts+ config_data['default_router']['file'] +" 0")
	time.sleep(10)
	print "\tWifi Disabled\n"
	toret = toret + "\tWifi Disabled\n"
	return toret
#Log functions
def log_show():
	try:
		log = open(log_file, 'r')
	except IOError:
		print "\n-->An error has been occurred when the system open the log\n"
		wait()
		return 1
	else:
		print "\n" + log.read() + "\n"
		wait()
		log.close()
		return 0


if pre_main()!=0:
	logging.critical("Critical failure in the initial program load. Program is forced to stop")
	print "\n-->An error has been occurred and the program can't initialize\n"
	wait()
	exit(1)
else:
	main()
	
