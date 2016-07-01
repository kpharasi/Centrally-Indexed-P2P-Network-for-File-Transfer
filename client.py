import socket
import os
import cPickle as pickle
import random
from thread import *
import platform
import time

# Server Information
serverPort = 7734
#serverName = socket.gethostname()
serverName = '152.14.142.29'

client_RFC_list = {}	# The RFCs that the client has currently

# Connecting to Server
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSocket.connect((serverName,serverPort))

client_port_num = 60000 + random.randint(1,1000)
#client_hostname = socket.gethostname()+str(client_port_num)
client_hostname = '10.139.62.135'

# Making RFC list
rfcs = [f for f in os.listdir(os.getcwd()+'/RFC/')]

for r in rfcs:
	num,title = r.split('_')
	client_RFC_list[num]=title

initial_add_requests = ""

for rfc,title in client_RFC_list.iteritems():
	message = "ADD "+str(rfc)+" P2P-CI/1.0\n"\
			  "Host: "+str(client_hostname)+"\n"\
			  "Port: "+str(client_port_num)+"\n"\
			  "Title: "+str(title)+"\n"
	initial_add_requests = initial_add_requests + message
#Sending intial add request messages to the server

print "Initial Add Requests Sent by Client"
print initial_add_requests

list_of_information = [client_port_num,client_hostname,client_RFC_list,initial_add_requests]

data = pickle.dumps(list_of_information,-1)

clientSocket.send(data)
clientSocket.close

#create add request message sent by client to server
def create_add_request(client_rfc_num,client_rfc_title):

	message = "ADD "+str(client_rfc_num)+" P2P-CI/1.0\n"\
			  "Host: "+str(client_hostname)+"\n"\
			  "Port: "+str(client_port_num)+"\n"\
			  "Title: "+str(client_rfc_title)

	return message

#create lookup request message sent by client to server

def create_lookup_request(client_rfc_num, client_rfc_title):

	message = "LOOKUP "+str(client_rfc_num)+" P2P-CI/1.0\n"\
			  "Host: "+str(client_hostname)+"\n"\
			  "Port: "+str(client_port_num)+"\n"\
			  "Title: "+str(client_rfc_title)
	return message

#create get request message sent from peer to peer

def create_get_request(client_rfc_num):

	message = "GET "+str(client_rfc_num)+" P2P-CI/1.0\n"\
			  "Host: "+str(client_hostname)+"\n"\
			  "OS: "+platform.platform()

	print "GET Request sent by Download Peer"
	print message

	return message

#create list request message sent from client to server

def create_list_request():

	message = "LIST ALL P2P-CI/1.0\n"\
			  "Host: "+str(client_hostname)+"\n"\
			  "Port: "+str(client_port_num)

	return message

#create get response message sent from peer to peer

def create_get_response(rfc_num,rfc_title):
	current_path = os.getcwd()
	message_list = []
	filename = current_path+"/RFC/"+str(rfc_num)+"_"+str(rfc_title)+".txt"
	current_time = time.strftime("%a, %d %b %Y %X %Z", time.localtime())
	if os.path.isfile(filename):
		content_length = os.path.getsize(filename)
		message = "P2P-CI/1.0 200 OK\n"\
			  	  "Date: "+str(current_time)+"\n"\
			  	  "OS: "+str(platform.platform())+"\n"\
			  	  "Last-Modified: "+str(time.ctime(os.path.getmtime(filename)))+"\n"\
			  	  "Content-Length:"+str(content_length)+"\n"\
			  	  "Content-Type: text/text \n"
	else:
		message = "P2P-CI/1.0 404 Not Found\n"\
				  "Date: "+str(current_time)+"\n"\
				  "OS: "+str(platform.platform())+"\n"
		print "GET Response Message sent by Upload Peer"
		print message
		message_list.append(message)
		return message_list

	print "GET Response Message sent by Upload Peer"
	data_stream = open(filename,'r')
	data = data_stream.read()
	print message+str(data)
	message_list.append(message)
	message_list.append(data)

	return message_list


#handle the response received from peer for a get message
def p2p_get_request(rfc_num,rfc_title,host,port):
	clientSocketP2P = socket.socket()
	clientSocketP2P.connect((host,int(port)))
	req_message = create_get_request(rfc_num)
	req_message_list = [req_message]
	req_message_list.append(rfc_title)
	req_pickle = pickle.dumps(req_message_list,-1)
	clientSocketP2P.send(req_pickle)
	response_received = pickle.loads(clientSocketP2P.recv(1024))
	print "GET Response Message received by Download Peer"
	if len(response_received) == 1:
		print response_received[0]
	else:
		print str(response_received[0])+str(response_received[1])
		current_path = os.getcwd()
		filename = current_path+"/RFC/"+str(rfc_num)+"_"+str(rfc_title)+".txt"
		with open(filename,'w') as file:
			file.write(response_received[1])
	clientSocketP2P.close()

#start a new thread which listens to download requests from other peers
def p2p_transfer_thread():
	uploadSocket = socket.socket()
	host = socket.gethostname()
	uploadSocket.bind((client_hostname,client_port_num))
	uploadSocket.listen(5)
	while 1:
		print "Inside P2p server thread"
		downloadSocket,downloadAddr = uploadSocket.accept()
		get_message_received = downloadSocket.recv(1024)
		get_message_list = pickle.loads(get_message_received)
		message_received = get_message_list[0]
		print "GET message received by Upload-Peer"
		print message_received
		rfc_title = get_message_list[1]
		message_list = message_received.split('\n')
		rfc_line = message_list[0].split()
		rfc_num = rfc_line[1]
		get_response_list = create_get_response(rfc_num,rfc_title)
		response_pickle = pickle.dumps(get_response_list,-1)
		downloadSocket.send(response_pickle)
		downloadSocket.close()

def user_input():
	print "Enter if you want to: ADD, GET, LIST, LOOKUP or EXIT:"
	service = raw_input()
	if service == "ADD":
		print "Enter RFC Number"
		client_rfc_num = raw_input()
		print "Enter Title"
		client_rfc_title = raw_input()
		current_path = os.getcwd()
		rfc_filename = current_path+"/RFC/"+str(client_rfc_num)+"_"+str(client_rfc_title)+".txt"
		if os.path.isfile(rfc_filename):
			req_message = create_add_request(client_rfc_num,client_rfc_title)
			print "ADD Request Message Sent by Client"
			print req_message
			clientSocket.send(bytes(req_message))
			response_received = clientSocket.recv(1024)
			print "ADD Response Message Received by Clinet"
			print response_received
		else:
			print "File not present with the client"
		user_input()

	elif service == "GET":
		print "Enter RFC Number"
		client_rfc_num = raw_input()
		print "Enter Title"
		client_rfc_title = raw_input()
		info_message = "GET\n"+str(client_rfc_num)+"\n"+str(client_hostname)+"\n"+str(client_port_num)+"\n"+str(client_rfc_title)
		clientSocket.send(info_message)
		response_received = clientSocket.recv(1024)
		response_list = pickle.loads(response_received)
		if len(response_list) == 1:
			print response_list[0]
		else:
			p2p_get_request(client_rfc_num,client_rfc_title,response_list[0],response_list[1])
		user_input()

	elif service == "LIST":
		req_message = create_list_request()
		print "LIST Request message sent by Client"
		print req_message
		clientSocket.send(bytes(req_message))
		response_received = clientSocket.recv(1024)
		print "LIST Response message received by Client"
		print response_received
		user_input()

	elif service == "LOOKUP":
		print "Enter RFC Number"
		client_rfc_num = raw_input()
		print "Enter Title"
		client_rfc_title = raw_input()
		req_message = create_lookup_request(client_rfc_num, client_rfc_title)
		print "LOOKUP Request message sent by Client"
		print req_message
		clientSocket.send(bytes(req_message))
		response_received = clientSocket.recv(1024)
		print "LOOKUP Response message received by Client"
		print response_received
		user_input()

	elif service == "EXIT":
		message = "EXIT"
		clientSocket.send(message)
		print "Client EXIT message sent"
		clientSocket.close()
#start the thread which listens to download requests from other clients
start_new_thread(p2p_transfer_thread, ())
user_input()