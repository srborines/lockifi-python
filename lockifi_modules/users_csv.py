# Codigo 11.7: users_csv.py: Module to save and read users on a csv file
 
#! /usr/bin/env python
# encoding: latin1
 
import csv
import logging
 
def save_users(filename, users):
	users_save = []
	try:
		file = open(filename, "w")
		file_csv = csv.writer(file)
		for user in users:
			users_save.append([user['name'],user['accountId']])
		file_csv.writerows(users_save)
	except IOError:
		logging.critical("[save_users()] doesnt exist users file(users.csv)")
		return -1
	else:
		file.close()
		return 0
 
def read_users(filename):
	users = []
	try:
		file = open(filename, "r")
		file_csv = csv.reader(file)
		for name,accountId in file_csv:
			users.append({"name": name, "accountId": accountId, "status": "unknow"})
	except IOError:
		logging.critical("[read_users()] doesnt exist users file(users.csv)")
		return -1
	except ValueError:
		users = []
	else:
		file.close()
		return users
	