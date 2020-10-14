# http://docs.openstack.org/developer/python-novaclient/ref/v2/servers.html
import time, os, sys
import inspect
from os import environ as env
import argparse

from  novaclient import client
import keystoneclient.v3.client as ksclient
from keystoneauth1 import loading
from keystoneauth1 import session

parser = argparse.ArgumentParser(description="Deploy an instance")

parser.add_argument('--flavor', type=str, nargs='?', default="ssc.xsmall")
parser.add_argument('--private_network', type=str, nargs='?', default="UPPMAX 2020/1-2 Internal IPv4 Network")
parser.add_argument('--public_network', type=str, nargs='?', default= "Public External IPv4 Network")
parser.add_argument('--image_name', type=str, nargs='?', default= "Ubuntu 18.04")
parser.add_argument('--cloudinit', type=str, nargs='?')
parser.add_argument('--security_group', type=str, action='append', default=['default'])
parser.add_argument('--num_instances', type=int, nargs='?', default=1)
parser.add_argument('instance_name', type=str)
parser.add_argument('key_name', type=str)

args = parser.parse_args()

loader = loading.get_plugin_loader('password')

auth = loader.load_from_options(auth_url=env['OS_AUTH_URL'],
                                username=env['OS_USERNAME'],
                                password=env['OS_PASSWORD'],
                                project_name=env['OS_PROJECT_NAME'],
                                project_domain_name=env['OS_USER_DOMAIN_NAME'],
                                project_id=env['OS_PROJECT_ID'],
                                user_domain_name=env['OS_USER_DOMAIN_NAME'])

sess = session.Session(auth=auth)
nova = client.Client('2.1', session=sess)
print("user authorization completed.")

image = nova.glance.find_image(args.image_name)

flavor = nova.flavors.find(name=args.flavor)

if args.private_network != None:
    net = nova.neutron.find_network(args.private_network)
    nics = [{'net-id': net.id}]
else:
    sys.exit("private-net not defined.")

for i in range(1, args.num_instances+1):
    print("Creating instance %i... " % i)
    if args.num_instances == 1:
        instance_name = args.instance_name
    else: 
        instance_name = args.instance_name + str(i)

    with open(args.cloudinit) as cloudinit:
        instance = nova.servers.create(
                name=instance_name, 
                key_name=args.key_name, 
                image=image, 
                flavor=flavor, 
                userdata=cloudinit, 
                nics=nics,
                security_groups=args.security_group)

    inst_status = instance.status
    print("waiting for 10 seconds.. ")
    time.sleep(10)

    while inst_status == 'BUILD':
        print("Instance: "+instance.name+" is in "+inst_status+" state, sleeping for 5 seconds more...")
        time.sleep(5)
        instance = nova.servers.get(instance.id)
        inst_status = instance.status

    print("Instance: "+ args.instance_name +" is in " + inst_status + "state")
