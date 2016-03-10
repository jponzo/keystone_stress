import requests
import sys
import random
import os
import Queue
import threading
import json

#################################
users_qty=int(sys.argv[1])      #
tokens_per_user=int(sys.argv[2])# 
user_create_paralell=False      #
user_delet_parallel=False       #
#################################

global users_dict
users_dict = {}

def generate_user():
	user = "test_" + random_string(5)
	password = random_string(8)
	global users_dict
	users_dict[user] = password
	return user,password

def create_keystone_user(username, password):
	create_string = 'keystone --os-endpoint http://KEYSTONE-EP:35357/v2.0 --os-token OS_TOKEN user-create --pass %s --tenant tenantName --name %s' % (password, username)
	os.system(create_string)

def delete_keystone_user(username,shit):
	delete_string = 'keystone --os-endpoint http://KEYSTONE-EP:35357/v2.0 --os-token OS_TOKEN user-delete ' + username 
	status_code = os.system(delete_string)
	if status_code != "":
		status_code = "%s DELETED" % username
	else:
		status_code = "%s FAILED TO DELETE" % username
	return status_code

def get_token(username, password):
   tenantname = "tenantName"
   _body = '{"auth":{"tenantName": "%s", "passwordCredentials":{"username": "%s", "password": "%s"}}}' % (tenantname, username, password)
   r = requests.post('http://KEYSTONE-EP:35357/v2.0/tokens', headers = {'Content-Type': 'application/json'}, data=_body)
   status_code = r.status_code
   if status_code == 200:
	token_id = r.json()['access']['token']['id']
   else:
	token_id = None
   return status_code,token_id

def random_string(length):
    number = '0123456789'
    alpha = 'abcdefghijklmnopqrstuvwxyz'
    id = ''
    for i in range(0,length,2):
        id += random.choice(number)
        id += random.choice(alpha)
    return id

#CREATE USERS
print "\nCREATING %s USERS...\n" % users_qty

if user_create_paralell:
	#CONCURRENT
	threads_list=[]
	for i in range(users_qty):
		user, password = generate_user()
		threads_list.append(threading.Thread(target=create_keystone_user, args=(user,password)))
	
	for mythread in threads_list: 
		print mythread
		mythread.daemon = True
		mythread.start()
	
	for mythread in threads_list:
		mythread.join()
else:	
	#SERIALIZED
	for i in range(users_qty):
	        user, password = generate_user()
		create_keystone_user(user,password)
#dump users to file
json.dump(users_dict, open("users.json",'w'))
	
#GET TOKEN
for i in range(tokens_per_user):
	print "\nGETTING %s TOKENS PER USER...\n" % tokens_per_user
	tokenget_threads = []

	for user in users_dict.keys():
		tokenget_threads.append(threading.Thread(target=get_token, args=(user, users_dict[user])))
	
	for mythread2 in tokenget_threads:
	        print mythread2
	        mythread2.daemon = True
	        mythread2.start()
	
	for mythread2 in tokenget_threads:
		mythread2.join()
	
#DELETE USERS
print "\nDELETING USERS...\n"
#PARALLEL
if user_delet_parallel:
	userdelete_threads = []
	for user2delete in users_dict.keys():
		print user2delete
	        userdelete_threads.append(threading.Thread(target=delete_keystone_user, args=(user2delete,"test")))
	
	for mythread3 in userdelete_threads:
	        print mythread3
	        mythread3.daemon = True
	        mythread3.start()
else:
        #SERIALIZED
	for user2delete in users_dict.keys():
                delete_keystone_user(user2delete)
