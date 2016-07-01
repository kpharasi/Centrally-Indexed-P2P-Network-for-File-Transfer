import socket
import cPickle as pickle
import random
from thread import *
import platform
import time

# Server Information
serverPort = 7734
#serverName = socket.gethostname()
serverName = '152.14.142.29'

#Binding the serverport to 7734
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind((serverName,serverPort))

#listening to requests from clients
serverSocket.listen(5)

print 'The server is ready'

index_dict = {}      #stores a dict which contains the key as rfc number and key as list of peers who are currently sharing the RFC
rfc_title_dict = {}	 #stores a dict which contains the key as rfc number and value as rfc title
active_peer_dict = {} #stores a dict which contains the key as hostname/ip address and value as the port on which it connects to server. Only active clients are present.


#creates the add response message which is sent from server to client
def create_add_response_message(port_num,hostname,rfc_num,rfc_title):

	message = "P2P-CI/1.0 200 OK\n"\
			  ""+str(rfc_num)+" "+str(rfc_title)+" "+str(hostname)+" "+str(port_num)

	return message

#creates the list response message which is sent from server to client
def create_list_response_message(index_dict, rfc_title_dict, active_peer_dict):

	message = "P2P-CI/1.0 200 OK"\

	list_of_rfc = []
	for key,value in index_dict.iteritems():
		for v in value:
			temp_message = str(key)+" "+str(rfc_title_dict.get(key))+" "+str(v)+" "+str(active_peer_dict.get(v))
			list_of_rfc.append(temp_message)

	for l in list_of_rfc:
			message = message + "\n" + l

	return message

#creates the lookup response message which is sent from server to client
#if no rfc is present with the provided rfc number then it returns 404 not found message
def create_lookup_response_message(index_dict, rfc_title_dict, active_peer_dict, rfc_num, rfc_title):
	list_of_hosts = index_dict.get(rfc_num)
	if list_of_hosts:
		message = "P2P-CI/1.0 200 OK"
		for host in list_of_hosts:
			temp_message = str(rfc_num)+" "+str(rfc_title)+" "+str(host)+" "+str(active_peer_dict.get(host))
			message = message + "\n" + temp_message
	else:
		message = "P2P-CI/1.0 404 Not Found"

	return message

#deletes the entries from the datastructures when a host leaves the server
def delete_index_dict(index_dict,rfc_title_dict,hostname):
	list_of_rfc = []
	
	for rfc,hosts in index_dict.iteritems():
		if hostname in hosts:
			hosts.remove(hostname)
			if len(hosts)==0:
				list_of_rfc.append(rfc)

	for l in list_of_rfc:
		index_dict.pop(l,None)
		rfc_title_dict.pop(l,None)

	return index_dict, rfc_title_dict

def delete_active_peer_dict(active_peer_dict,hostname):

	active_peer_dict.pop(hostname,None)
	return active_peer_dict

#lookup to check if a particular rfc number is present with any client
def lookup_rfc(rfc_num,rfc_title_dict):
	if str(rfc_num) in rfc_title_dict.keys():
		return True
	return False

#creates the get response message.
#if a rfc is present then it returns the hostname and port number of the peer who has the file
#if the rfc is not present with any server then it returns 404 message
def create_get_response_message(index_dict,rfc_title_dict,active_peer_dict,rfc_num,rfc_title,exists):

	get_response_list = []

	if not exists:
		current_time = time.strftime("%a, %d %b %Y %X %Z", time.localtime())
		message = "P2P-CI/1.0 404 Not Found\n"\
				  "Date: "+str(current_time)+"\n"\
				  "OS: "+str(platform.platform())+"\n"
		get_response_list.append(message)
	else:
		list_of_hosts = index_dict.get(rfc_num)
		host = list_of_hosts[0]
		port = active_peer_dict.get(host)
		get_response_list.append(host)
		get_response_list.append(port)
	return get_response_list

#creates a new thread to handle each client
def client_init(connectionsocket, addr):
	global active_peer_dict, index_dict, rfc_title_dict
	information = connectionsocket.recv(1024)
	information_list = pickle.loads(information)
	port_num = information_list[0]
	hostname = information_list[1]
	rfc_list = information_list[2]
	initial_add_requests = information_list[3]

	print "Initial Add Requests received by Server"
	print initial_add_requests

	active_peer_dict[hostname]=port_num

	for num,title in rfc_list.iteritems():
		rfc_title_dict[num]=title
		if num in index_dict:
			current_host_list = index_dict.get(num)
			current_host_list.append(hostname)
		else:
			index_dict[num]=[hostname]
	print "New client connected. Below are data structures"
	print index_dict
	print rfc_title_dict
	print active_peer_dict

	while 1:
		message_received = connectionsocket.recv(1024)
		if message_received[0]== 'E':
			print "EXIT message recieved by Server"
			break
		elif message_received[0] == 'A':
			print "ADD Request Message Received by Server"
			print message_received
			message_list = message_received.split('\n')
			rfc_line = message_list[0].split()
			rfc_num = rfc_line[1]
			host_line = message_list[1].split()
			hostname = host_line[1]
			port_line = message_list[2].split()
			port_num = port_line[1]
			title_line = message_list[3].split()
			rfc_title = title_line[1]
			if rfc_num in index_dict:
				current_host_list = index_dict.get(rfc_num)
				current_host_list.append(hostname)
			else:
				index_dict[rfc_num] = [hostname]
			rfc_title_dict[rfc_num] = rfc_title+".txt"
			add_response_message = create_add_response_message(port_num,hostname,rfc_num,rfc_title)
			print "ADD Response Message Sent by Server"
			print add_response_message
			connectionsocket.send(add_response_message)
			print "New RFC added. Below are the data structures"
			print index_dict
			print rfc_title_dict
		
		elif message_received[0] == "L":
			if message_received[1] == "I":
				print "LIST Request Message Received by Server"
				print message_received
				message_list = message_received.split('\n')
				host_line = message_list[1].split()
				hostname = host_line[1]
				port_line = message_list[2].split()
				port_num = port_line[1]
				list_response_message = create_list_response_message(index_dict, rfc_title_dict, active_peer_dict)
				print "LIST Response Message Sent by Server"
				print list_response_message
				connectionsocket.send(list_response_message)
			else:
				print "LOOKUP Request Message Received by Server"
				print message_received
				message_list = message_received.split('\n')
				port_line = message_list[2].split()
				port_num = port_line[1]
				host_line = message_list[1].split()
				hostname = host_line[1]
				rfc_line = message_list[0].split()
				rfc_num = rfc_line[1]
				title_line = message_list[3].split()
				rfc_title = title_line[1]
				lookup_response_message = create_lookup_response_message(index_dict, rfc_title_dict, active_peer_dict, rfc_num, rfc_title)
				print "LOOKUP Response Message Sent by Server"
				print lookup_response_message
				connectionsocket.send(lookup_response_message)
		elif message_received[0] == "G":
				message_list = message_received.split('\n')
				port_num = message_list[3]
				hostname = message_list[2]
				rfc_num = message_list[1]
				rfc_title = message_list[4]
				exists = lookup_rfc(rfc_num,rfc_title_dict)
				get_response_list = create_get_response_message(index_dict,rfc_title_dict,active_peer_dict,rfc_num,rfc_title,exists)
				connectionsocket.send(pickle.dumps(get_response_list,-1))		

	index_dict,rfc_title_dict = delete_index_dict(index_dict,rfc_title_dict,information_list[1])

	print "Client Exited Below are the data structures"
	print index_dict
	print rfc_title_dict

	active_peer_dict=delete_active_peer_dict(active_peer_dict,information_list[1])

	print active_peer_dict
	connectionsocket.close()

while 1:
	connectionsocket, addr = serverSocket.accept()
	start_new_thread(client_init, (connectionsocket, addr))
serverSocket.close()