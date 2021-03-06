import socket
import sys

if len(sys.argv) < 2 or sys.argv[1] != '-m':
	print 'Invalid usage'
	sys.exit(0)


host = '<broadcast>'
port = 60000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
server_address = (host, port)

mac_address = sys.argv[2]
sock.sendto(mac_address, server_address)

data, server = sock.recvfrom(1024)
sock.close()
if data == 'invalid MAC':
	print 'Invalid MAC address sent'
elif data == 'No space':
	print 'No space for desired IP'
else:
	addresses = data.split()
	print 'IP Address with CIDR: ' + addresses[0]
	print 'Network Address: ' + addresses[1]
	print 'Broadcast address: ' + addresses[2]
	print 'Sample Gateway: ' + addresses[3]
	print 'Sample DNS: ' + addresses[4]
