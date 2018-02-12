import socket
import sys
import signal
import threading
import config as config


class ProxyServer:
	""" The proxy server class """

	def __init__(self, config):
		""" Intialiser function for ProxyServer class """

		# Register shutdown handler with SIGINT (Ctrl + c)
		signal.signal(signal.SIGINT, self.shutdown_handler)

		# Create a TCP socket
		self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

		# Bind the socket to the host and the port.
		self.serverSocket.bind((config.HOST_NAME, config.BIND_PORT))

		# Limit the maximum number of connections to 10
		self.serverSocket.listen(config.MAX_CONNECTIONS)

		# Initialise the clients dictionary
		self.__clients = {}

		print ('The proxy server is running on port ' + str(config.BIND_PORT))


	def start_listening(self):
		""" Start listening on the mentioned port number for client connections """

		# Infinite loop until SIGINT is fired.
		while True:
			# Establish connection
			(client_socket, client_address) = self.serverSocket.accept()

			# Create a proxy thread for the established connection
			thread = threading.Thread(name=self._getClientName(client_address), target=self.proxy_thread, args=(client_socket, client_address))
			thread.setDaemon(True)
			thread.start()

		self.shutdown_handler(0,0)


	def proxy_thread(self, conn, client_addr):
		"""
			A thread which is acting as a proxy between the browser and the web server.
		"""

		# Receive request from the browser
		request = conn.recv(config.MAX_REQUEST_LEN)

		# Parse the first line
		first_line = request.decode().split('\n')[0]

		# Get URL
		url = first_line.split(' ')[1]

		# Copy the webserver address in http_pos by searching for '://'
		http_pos = url.find("://")
		if (http_pos == -1):
			temp = url
		else:
			temp = url[(http_pos + 3) : ]

		# Copy the port number in port by searching for ':' in the remaining address
		port_pos = temp.find(":")

		webserver_pos = temp.find("/")
		if webserver_pos == -1:
			webserver_pos = len(temp)

		webserver = ""
		port = -1

		# Set the port number to 80 (default) if not found
		if (port_pos == -1 or webserver_pos < port_pos):
			port = DEFAULT_PORT
			webserver = temp[:webserver_pos]
		else:
			port = int((temp[(port_pos + 1): ])[: webserver_pos - port_pos - 1])
			webserver = temp[: port_pos]

		try:
			# Connect to the web server through a new socket
			sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

			sck.settimeout(config.CONNECTION_TIMEOUT)
			sck.connect((webserver, port))

			# Send the received request from the browser to the web server
			sck.sendall(request.encode('utf-8'))

			# Redirect all responses from the web server to the browser
			while True:
			    data = sck.recv(config.MAX_REQUEST_LEN)
			    if len(data):
			        conn.send(data)
			    else:
			        break
			sck.close()
			conn.close()
		except socket.error as error_msg:
			print ('ERROR: ', client_addr,error_msg)
			if sck:
				sck.close()
			if conn:
				conn.close()


	def _getClientName(self, cli_addr):
		""" returns the Client Name on the basis of cli_addr """
		return "Client"


	def shutdown_handler(self, signum, frame):
		""" Handle the exiting server and clean all traces """
		self.serverSocket.close()
		sys.exit(0)


if __name__ == "__main__":
	server = ProxyServer(config)
	server.start_listening()
