import os
import socket
import sys

os.system('bash broadcast.sh')
broadcast_address = [line.rstrip('\n') for line in open('broadcast.txt')][0]

host = broadcast_address
# host = ''
port = 60000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
server_address = (host, port)

if sys.argv[1] != '-m':
	sys.exit(0)

mac_address = sys.argv[2]
sock.sendto(mac_address, server_address)

data, server = sock.recvfrom(1024)
print data
