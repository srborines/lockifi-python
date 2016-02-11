import ConfigParser
import logging

#Configuration functions
def import_configuration(conf_file):	
	cfg = ConfigParser.ConfigParser()
	if not cfg.read(conf_file):  
		logging.critical("[import_configuration()] doesnt exist configuration file(conf.cfg)")
		return -1
	if not cfg.has_section("Router"):
		logging.critical("[import_configuration()] doesnt exist section of Router on configuration file")
		return -1
	if not cfg.has_section("Latch"):
		logging.critical("[import_configuration()] doesnt exist section of Latch on configuration file")
		return -1
	if not cfg.has_section("Lockifi"):
		logging.critical("[import_configuration()] doesnt exist section of Latch on configuration file")
		return -1
	if not cfg.has_option("Latch","appid"):
		logging.critical("[import_configuration()] doesnt exist option appid on section of Latch on configuration file")
		return -1
	if not cfg.has_option("Latch","seckey"):
		logging.critical("[import_configuration()] doesnt exist option seckey on section of Latch on configuration file")	
		return -1
	if not cfg.has_option("Latch","users_file"):
		logging.critical( "[import_configuration()] doesnt exist option users_file on section of Latch on configuration file")	
		return -1
	if not cfg.has_option("Latch","routers_file"):
		logging.critical( "[import_configuration()] doesnt exist option routers_file on section of Latch on configuration file")	
		return -1
	if not cfg.has_option("Router","default_router_name"):
		logging.critical( "[import_configuration()] doesnt exist option default_router_name on section of Router on configuration file")	
		return -1
	if not cfg.has_option("Router","default_router_file"):
		logging.critical( "[import_configuration()] doesnt exist option default_router_file on section of Router on configuration file")	
		return -1
	if not cfg.has_option("Lockifi","listening_mode"):
		logging.critical( "[import_configuration()] doesnt exist option listening_mode on section of Lockifi on configuration file")	
		return -1
	appid = cfg.get("Latch", "appid")
	seckey = cfg.get("Latch", "seckey")
	users_file = cfg.get("Latch", "users_file")
	routers_file = cfg.get("Latch", "routers_file")
	
	default_router_name = cfg.get("Router", "default_router_name")
	default_router_file = cfg.get("Router", "default_router_file")
	
	listening_mode = cfg.get("Lockifi","listening_mode")
	config_data={'appid':appid,'seckey':seckey,'users_file':users_file,'routers_file':routers_file,'default_router':{'name':default_router_name,'file':default_router_file},'listening_mode':listening_mode}
	
	return config_data
def save_configuration(conf_file,section,option,value):
	cfg = ConfigParser.ConfigParser()
	if not cfg.read(conf_file):  
		logging.error("[save_configuration()] doesnt exist configuration file(conf.cfg)")
		return -1
	if not cfg.has_section(section):
		logging.error("[save_configuration()] doesnt exist section of "+ section +" on configuration file")
		return -1
	if not cfg.has_option(section,option):
		logging.error("[save_configuration()] doesnt exist option "+ option +" on section of "+ section +" on configuration file")
		return -1
	cfg.set(section, option, value)
	try:
		f = open(conf_file, "w")  
		cfg.write(f)
	except IOError:
		logging.error("[save_configuration()] doesnt exist configuration file(conf.cfg)")
		return -1
	else:
		f.close()
		return 0