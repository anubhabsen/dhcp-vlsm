import operator
import math
import socket

subnet_addresses = {}
broadcast_addresses = {}
subnet_masks = {}

def init_hosts():
	lines = [line.rstrip('\n') for line in open('subnets.conf')]
	# print lines

	base_address = lines[0].split('/')[0]
	bits_available = 32 - int(lines[0].split('/')[1])

	N = int(lines[1])

	lab_requests = {}
	mac_to_lab = {}

	for i in range(2, 2 + N):
		temp = lines[i].split(':')
		lab_requests[temp[0]] = int(temp[1])

	for i in range(2 + N, len(lines)):
		temp = lines[i].split('-')
		mac_to_lab[temp[0]] = temp[1]

	max_hosts = max((1 << bits_available) - 2 * (N + 1), 0)

	total_requests = 0

	for i in range(2, 2 + N):
		total_requests += int(lines[i].split(':')[1])

	sorted_labs = list(reversed(sorted(lab_requests.items(), key=operator.itemgetter(1))))

	if total_requests > max_hosts:
		print 'Due to unavailability of IP addresses only the following labs can be accommodated:'

	while total_requests > max_hosts:
		lab_name = sorted_labs[N - 1][0]
		total_requests -= lab_requests[lab_name]
		del lab_requests[lab_name]
		sorted_labs.pop()
		N -= 1

	print lab_requests
	print
	# print sorted_labs

	base_num = [int(x) for x in base_address.split('.')]
	base10 = 0
	for i in range(4):
		base10 += pow(256, i) * base_num[3 - i]

	for lab in sorted_labs:
		tempbase10 = base10
		addr = ''
		for i in range(4):
			if i == 0:
				addr = str(tempbase10 % 256) + addr
			else:
				addr = str(tempbase10 % 256) + '.' + addr
			tempbase10 /= 256

		subnet_addresses[lab[0]] = addr

		to_allocate = math.ceil(math.log(int(lab[1]) + 2, 2))
		subnet_masks[lab[0]] = '/' + str(int(32 - to_allocate))
		temp = int(pow(2, to_allocate))
		base10 += temp

		baddr = base10 - 1
		stbaddr = ''
		for i in range(4):
			if i == 0:
				stbaddr = str(baddr % 256) + stbaddr
			else:
				stbaddr = str(baddr % 256) + '.' + stbaddr
			baddr /= 256

		broadcast_addresses[lab[0]] = stbaddr

def listen():
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	# Bind the socket to the port
	server_address = ('localhost', 60000)
	sock.bind(server_address)

	while True:
		data, address = sock.recvfrom(1024)
		print data
		if data:
			sock.sendto(data, address)

if __name__ == "__main__":
	init_hosts()
	print subnet_masks
	print subnet_addresses
	print broadcast_addresses
	listen()
