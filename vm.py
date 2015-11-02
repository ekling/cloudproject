import os
import time
import fileinput
from novaclient.client import Client

def init():
    config = {'username':'klem2814',
              'api_key':'x1xv6565',
              'project_id':'ACC-Course',
              'auth_url':'http://smog.uppmax.uu.se:5000/v2.0'}

    return Client('2',**config)

def init_broker(nc):

    nc.keypairs.findall(name="emilKey")
    ubuntu_image = nc.images.find(name='CprojBrokerSnap')
    flavor = nc.flavors.find(name='m1.medium')

    userdata = open('userdata.yml', 'r')

    instance = nc.servers.create(name='EmilBroker', image=ubuntu_image, flavor=
                                flavor, key_name='emilKey', userdata=userdata)

    userdata.close()

    status = instance.status
    while status == 'BUILD':
        print 'Broker is building...'
        time.sleep(10)
        instance = nc.servers.get(instance.id)
        status = instance.status

    ips = nc.floating_ips.list()
    for ip in ips:
        if ((getattr(ip, 'instance_id')) == None):
                floating_ip = getattr(ip, 'ip')
                break

    ins = nc.servers.find(name='EmilBroker')
    ins.add_floating_ip(floating_ip)


    ### MODIFY WORKERDATA FILE ###
    float_ip = 'export BROKER_IP="' + str(floating_ip) + '"'

    with open('workerdata_init.yml', 'r') as file:
        f = file.read()
    f_updated = f.replace('brokerip', float_ip)

    with open('workerdata.yml', 'wb') as file:
        file.write(f_updated)

def init_worker(i, nc):

    nc.keypairs.findall(name="emilKey")
    worker_image = nc.images.find(name='G19_Worker_Image')
    flavor = nc.flavors.find(name='m1.medium')

    workerdata = open('workerdata.yml', 'r')

    instance = nc.servers.create(name='EmilWorker_' + str(i), image=worker_image, flavor=
                                flavor, key_name='emilKey', userdata=workerdata)

    status = instance.status
    while status == 'BUILD':
        print 'Worker_' + str(i) + ' is building...'
        time.sleep(5)
        instance = nc.servers.get(instance.id)
        status = instance.status
    ips = nc.floating_ips.list()
    for ip in ips:
        if ((getattr(ip, 'instance_id')) == None):
                floating_ip = getattr(ip, 'ip')
                break
    ins = nc.servers.find(name='EmilWorker_' + str(i))
    ins.add_floating_ip(floating_ip)

    workerdata.close()

if __name__ == '__main__':
    nc = init()
    NUMBER_OF_WORKERS = input('Number of workers: ')

    init_broker(nc)
    for i in range(1, NUMBER_OF_WORKERS + 1):
        init_worker(i,nc)
