import gevent
from gevent import Greenlet
from gevent import monkey; monkey.patch_socket()
import requests
import sys
import random
import os

STRESS_LEVEL = int(sys.argv[1])

global users_dict
users_dict = {}

def generate_user():
	user = "test_" + random_string(5)
	password = random_string(8)
	users_dict[user] = password
	return user,password

def create_keystone_user(username, password):
	create_string = 'keystone --os-endpoint http://KEYSTONE-EP:35357/v2.0 --os-token OS-TOKEN user-create --pass %s --tenant tenantName --name %s' % (password, username)
	os.system(create_string)

def delete_keystone_user(username):
	delete_string = 'keystone --os-endpoint http://KEYSTONE-EP:35357/v2.0 --os-token OS-TOKEN user-delete ' + username 
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
print "\nCREATING USERS...\n"
threads_list=[]
for i in range(STRESS_LEVEL):
	user, password = generate_user()
	threads_list.append(Greenlet.spawn(create_keystone_user, user, password))
threads_result = gevent.joinall(threads_list)

#GET TOKEN
print "\nGETTING TOKENS...\n"
tokenget_threads = []
for user in users_dict.keys():
	tokenget_threads.append(Greenlet.spawn(get_token, user, users_dict[user]))
threads_result = gevent.joinall(tokenget_threads)
for thread in tokenget_threads:
	print thread.value

#DELETE USERS

print "\nDELETING USERS...\n"
userdelete_threads = []
for user in users_dict.keys():
        userdelete_threads.append(Greenlet.spawn(delete_keystone_user, user))
threads_result = gevent.joinall(userdelete_threads)
for thread in userdelete_threads:
        print thread.value
