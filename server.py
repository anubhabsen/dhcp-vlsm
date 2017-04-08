lines = [line.rstrip('\n') for line in open('subnets.conf')]

base_address = (lines[0].split('/'))[0]

N = int(lines[1])

lab_capacities = {}
mac_to_lab = {}

for i in range(2, 2 + N):
	temp = lines[i].split(':')
	lab_capacities[temp[0]] = int(temp[1])

for i in range(2 + N, len(lines)):
	temp = lines[i].split('-')
	mac_to_lab[temp[0]] = temp[1]
