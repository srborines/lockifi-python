# Codigo 11.7: routers_csv.py: Module to save and read routers on a csv file
 
#! /usr/bin/env python
# encoding: latin1
 
import csv
import logging
 
def save_routers(filename, routers):
	routers_save = []
	try:
		file = open(filename, "w")
		file_csv = csv.writer(file)
		for router in routers:
			routers_save.append([router['name'],router['file']])
		file_csv.writerows(routers_save)
	except IOError:
		logging.critical("[save_routers()] doesnt exist routers file(routers.csv)")
		return -1
	else:
		file.close()
		return 0
 
def read_routers(filename):
	routers = []
	try:
		file = open(filename, "r")
		file_csv = csv.reader(file)
		for name, filename_router in file_csv:
			routers.append({"name": name, "file": filename_router})
	except IOError:
		logging.critical("[read_routers()] doesnt exist routers file(routers.csv)")
		return -1
	except ValueError:
	
		return -1
	else:
		file.close()
		return routers