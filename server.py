import operator
import math
import socket
import re
import sys

subnet_addresses = {}
broadcast_addresses = {}
subnet_masks = {}
mac_to_lab = {}
mac_to_curr_hosts = {}
N = 1
last_address = 0


def toipstring(num):
    addr = ''
    for i in range(4):
        if i == 0:
            addr = str(num % 256) + addr
        else:
            addr = str(num % 256) + '.' + addr
        num /= 256
    return addr

def tobase10(s):
    base_num = [int(x) for x in s.split('.')]
    base10 = 0
    for i in range(4):
        base10 += pow(256, i) * base_num[3 - i]
    return base10

def read_validate(lines):
    base_address = lines[0].split('/')[0]

    try:
        bits_available = 32 - int(lines[0].split('/')[1])
    except:
        print 'subnet mask is invalid. Please fix conf file'
        sys.exit(0)

    try:
        socket.inet_aton(base_address)
    except socket.error:
        print 'The base IP address provided is incorrect. Please fix conf file'
        sys.exit(0)

    try:
        N = int(lines[1])
    except:
        print 'Number of labs line is invalid. Please fix conf file'
        sys.exit(0)

    lab_requests = {}

    for i in range(2, 2 + N):
        temp = lines[i].split(':')
        try:
            lab_requests[temp[0]] = int(temp[1])
        except:
            print 'Error in the labs and number of hosts in each lab. Please fix conf file'
            sys.exit(0)

    for i in range(2 + N, len(lines)):
        temp = lines[i].split()
        if re.match("[0-9a-f]{2}([-:])[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", temp[0].lower()):
            mac_to_lab[temp[0]] = temp[1]
            mac_to_curr_hosts[temp[0]] = 1
        else:
            print 'Invalid MAC address in conf file. Please correct the MAC addresses'
            sys.exit(0)

    max_hosts = max((1 << bits_available) - 2 * (N + 1), 0)

    total_requests = 0

    for i in range(2, 2 + N):
        total_requests += int(lines[i].split(':')[1])

    to_add = 0
    for i in range(bits_available):
        to_add = to_add * 10 + 1

    last_address = toipstring(tobase10(base_address) + to_add)

    return [base_address, N, lab_requests, max_hosts, total_requests, bits_available, last_address]

def init_hosts():
    lines = [line.rstrip('\n') for line in open('subnets.conf')]

    read_data = read_validate(lines)

    base_address = read_data[0]
    N = read_data[1]
    lab_requests = read_data[2]
    max_hosts = read_data[3]
    total_requests = read_data[4]
    bits_available = read_data[5]
    last_address = read_data[6]

    sorted_labs = list(reversed(sorted(lab_requests.items(), key=operator.itemgetter(1))))

    if total_requests > max_hosts:
        print 'Due to unavailability of IP addresses only the following labs can be accommodated:'

    key_to_delete = []

    for key, value in lab_requests.iteritems():
        if value > max_hosts:
            lab_requests[key] = 0
            key_to_delete.append(key)
            total_requests -= value

    for k in key_to_delete:
        del lab_requests[k]

    sorted_labs = list(reversed(sorted(lab_requests.items(), key=operator.itemgetter(1))))

    while total_requests > max_hosts:
        if N >= 1:
            lab_name = sorted_labs[N - 1][0]
        else:
            print 'No IPs can be allocated due to lack of space'
            sys.exit(0)
        total_requests -= lab_requests[lab_name]
        del lab_requests[lab_name]
        sorted_labs.pop()
        N -= 1

    print lab_requests
    print
    base10 = tobase10(base_address)

    max_hosts = max((1 << bits_available) - 2 * (N + 1), 0)

    for lab in sorted_labs:
        subnet_addresses[lab[0]] = toipstring(base10)

        to_allocate = math.ceil(math.log(int(lab[1]) + 2, 2))
        subnet_masks[lab[0]] = '/' + str(int(32 - to_allocate))
        temp = int(pow(2, to_allocate))
        base10 += temp

        broadcast_addresses[lab[0]] = toipstring(base10 - 1)

    max_broad = 0
    for key, value in broadcast_addresses.iteritems():
        if max_broad < tobase10(value):
            max_broad = tobase10(value)
    max_broad = toipstring(max_broad)
    subnet_addresses['unknown-lab'] = toipstring(tobase10(max_broad) + 1)
    mac_to_curr_hosts['unknown-lab'] = 1

    subnet_addresses['unknown-lab'] = toipstring(base10)
    to_allocate = math.ceil(math.log(max_hosts - total_requests, 2))
    subnet_masks['unknown-lab'] = '/' + str(int(32 - to_allocate))
    # print 'allocate', to_allocate
    temp = int(pow(2, to_allocate))
    base10 = tobase10(max_broad) + temp
    # broadcast_addresses['unknown-lab'] = last_address
    broadcast_addresses['unknown-lab'] = toipstring(tobase10(base_address) + pow(2, bits_available + 1) - 1)


def listen():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Bind the socket to the port
    server_address = ('', 60000)
    sock.bind(server_address)

    while True:
        mac, address = sock.recvfrom(17)
        if mac:
            if re.match("[0-9a-f]{2}([-:])[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", mac.lower()):
                if mac in mac_to_lab.keys():
                    lab_name = mac_to_lab[str(mac)]
                else:
                    new_ip_increment = mac_to_curr_hosts['unknown-lab'] + 1
                    new_ip = toipstring(tobase10(subnet_addresses['unknown-lab']) + new_ip_increment)
                    saddr = subnet_addresses['unknown-lab']
                    baddr = broadcast_addresses['unknown-lab']
                    if tobase10(subnet_addresses['unknown-lab']) + new_ip_increment >= tobase10(baddr):
                        print 'No space for more hosts.'
                        sock.sendto('No space', address)
                        continue
                    mask = subnet_masks['unknown-lab']
                    baseplusone = toipstring(tobase10(saddr) + 1)

                    sock.sendto(new_ip + mask + ' ' + saddr + ' ' + baddr + ' ' + baseplusone + ' ' + baseplusone, address)
                    mac_to_curr_hosts['unknown-lab'] += 1
                    # print subnet_addresses['unknown-lab'], mac_to_curr_hosts['unknown-lab']
                    continue

                new_ip_increment = mac_to_curr_hosts[str(mac)] + 1
                new_ip = toipstring(tobase10(subnet_addresses[lab_name]) + new_ip_increment)
                saddr = subnet_addresses[lab_name]
                baddr = broadcast_addresses[lab_name]
                if tobase10(subnet_addresses[lab_name]) + new_ip_increment >= tobase10(baddr):
                    print 'No space for more hosts.'
                    sock.sendto('No space', address)
                    continue
                mask = subnet_masks[lab_name]
                baseplusone = toipstring(tobase10(saddr) + 1)

                sock.sendto(new_ip + mask + ' ' + saddr + ' ' + baddr + ' ' + baseplusone + ' ' + baseplusone, address)
                mac_to_curr_hosts[str(mac)] += 1
            else:
                sock.sendto('invalid MAC', address)
                print 'invalid MAC address received. Please resend a correct one.'

if __name__ == "__main__":
    init_hosts()
    print subnet_masks
    print subnet_addresses
    print broadcast_addresses
    print mac_to_lab
    # print toipstring(tobase10('10.220.64.0') + pow(2, 15) - 1)
    print
    listen()
