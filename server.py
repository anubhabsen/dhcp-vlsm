lines = [line.rstrip('\n') for line in open('subnets.conf')]

base_address = (lines[0].split('/'))[0]
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

max_hosts = (1 << bits_available) - 2 * (N + 1)

total_requests = 0

for i in range(2, 2 + N):
	total_requests += int(lines[i].split(':')[1])

while total_requests > max_hosts:
	max_requests_from_lab = 0
	index_of_max = -1
	for key, value in lab_requests.iteritems():
		if value > max_requests_from_lab:
			max_requests_from_lab = value
			index_of_max = key

	lab_requests[index_of_max] -= 1

	total_requests -= 1
