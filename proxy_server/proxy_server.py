import socket
import sys
import signal
import threading
import config as config

class ProxyServer:
	'''
	Class for main proxy server
	'''

	def close_socket(self):
		self.server_socket.close()
		return

	def __init__(self, config):
		print('Initialising TCP/IPv4 socket connection')
		self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		# Reusing the already open Socket to avoid irritating errors
		self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

		print('Binding socket to port %s and host %s' %
			(config.BIND_PORT, config.HOST_NAME))
		self.server_socket.bind((config.HOST_NAME, config.BIND_PORT))

		print('Listen to the specified port %s' % config.BIND_PORT)
		self.server_socket.listen(config.MAX_CONNECTIONS)

		signal.signal(signal.SIGTERM, self.close_socket)
		return

	def __parse_request_header(self, request):
		# Splitting request
		split_req = request.split(' ')

		method = split_req[0]
		url = split_req[1]
		http_ver = split_req[2]

		return method, url, http_ver

	def start_accepting(self):

		# Forever accept
		while True:
			(client_socket, addr) = self.server_socket.accept()

			print('\n================REQUEST INITIATED==================\n')
			print('Receiving request from Client')
			client_req = client_socket.recv(config.MAX_REQUEST_LEN).decode()

			print('Separating client request line by line')
			parsed_req = client_req.split(config.JOIN_DELIM)

			# Parsing the First line of HTTP request header
			print('Parsing')
			print(parsed_req[0])
			req_method, req_url, req_http_ver = self.__parse_request_header(
																parsed_req[0]
																	);

			# Printing parsed information
			print(req_method)
			print(req_url)
			print(req_http_ver)

			# Calculating the start of host name
			host_start_pos = req_url.find(config.HTTP_REQUEST) +\
			 					len(config.HTTP_REQUEST)
			# Calculating the end of host name
			host_end_pos = req_url.find(config.HOST_DELIMITER, host_start_pos)
			# Calculating start of Port number
			port_start_pos = host_end_pos + 1
			# Calculating start of Host number
			port_end_pos = req_url.find(config.PORT_DELIMITER, port_start_pos)

			# Printing Host Name
			print('HOST NAME:')
			req_host_name = req_url[host_start_pos: host_end_pos]
			print(req_host_name)
			# Printing Port Name
			print('PORT NUMBER:')
			req_port_num = req_url[port_start_pos: port_end_pos]
			print(req_port_num)
			# Printing File Name
			print('FILE NAME:')
			req_file_name = req_url[port_end_pos + 1 : ]
			print(req_file_name)

			try:
				# Forming request
				print('Forming Request to original host')
				parsed_req[0] = '%s /%s %s' % (req_method, req_file_name, req_http_ver)
				print(parsed_req[0])
				host_req = config.JOIN_DELIM.join(parsed_req)

				# Initialising connection to the Requested Host Socket
				host_socket = socket.socket()
				host_socket.connect((req_host_name, int(req_port_num)))

				# Forwarding Request to Host
				print('requesting to the Host')
				host_socket.send(host_req.encode())

				# Receiving request from Host
				host_resp = host_socket.recv(config.MAX_REQUEST_LEN)
				# Forwarding request from Host to Client
				client_socket.send(host_resp)

				data = host_socket.recv(config.MAX_REQUEST_LEN)
				while  data:
					client_socket.send(data)
					data = host_socket.recv(config.MAX_REQUEST_LEN)

				print('Client request fulfilled..!!')
			except Exception as err:
				print('Unexpected Error Occurred on Connecting to Host')
				print(err)
			# Closing the Host Sockets
			host_socket.close()
			# Closing the Client Sockets
			client_socket.close()
			print('\n=================REQUEST TERMINATED==================\n')

if '__main__' == __name__:
	server = ProxyServer(config)
	server.start_accepting()
