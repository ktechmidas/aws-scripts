#!/usr/bin/python
import argparse
import boto.ec2
import sys
import argparse
import time
parser = argparse.ArgumentParser()
parser.add_argument("region")
parser.add_argument("instype")
parser.add_argument("ostype")
parser.add_argument("--ttl", default=0)
parser.add_argument("--price")
parser.add_argument("--instance")
parser.add_argument("--image")
parser.add_argument("--userdata")
parser.add_argument("--security")
args = parser.parse_args()

def deploy_ec2_instances_spot(region):
	if args.userdata:
		with file(args.userdata) as openfile:
			userdata_contents = openfile.read()
	else:
		userdata_contents = ""

	print "INFO: Now bringing up spot instance"
	ec2_conn = boto.ec2.connect_to_region(region)
	req = ec2_conn.request_spot_instances(price=args.price,instance_type=args.instance,image_id=args.image,key_name='web-sg-sorry', security_group_ids=[args.security],user_data=userdata_contents)

	print "INFO: Sleeping for a while to allow instances to come up"
	time.sleep(300)
	#Wait until the spot instance comes up, get it's ID.
	job_instance_id = None
	while job_instance_id == None:
		print "INFO: Getting Instance ID"
		job_sir_id = req[0].id # spot instance request = sir, job_ is the relevant aws item for this job
		reqs = ec2_conn.get_all_spot_instance_requests()
		for sir in reqs:
			if sir.id == job_sir_id:
				job_instance_id = sir.instance_id
				if job_instance_id: 
					print "job instance id: " + str(job_instance_id)
					instance_id = str(job_instance_id)
				else:
					print "Instance hasn't come up - Please investigate"	
 					sys.exit(-1)
	
	reservation = ec2_conn.get_all_instances(instance_id)
	instance = reservation[0].instances[0]
	while instance.update() != "running":
		print "INFO: Instance not yet running. Waiting a while"
		time.sleep(30)
	instance.add_tag("Farm",args.ttl)
	print "IP Addr: "+instance.ip_address

def deploy_ec2_instances_demand(region):
	ec2_conn = boto.ec2.connect_to_region(region)
	if args.ostype == "windows":
		reservation = ec2_conn.run_instances(image_id=args.image,instance_type=args.instance,security_group_ids=[args.security])
	else:
		reservation = ec2_conn.run_instances(image_id=args.image,instance_type=args.instance,security_group_ids=[args.security],key_name='web-sg-sorry')
	time.sleep(5)
	instance = reservation.instances[0]
	while instance.update() != "running":
		print "INFO: Instance not yet running. Waiting a while"
		time.sleep(30)
	instance.add_tag("Farm",args.ttl)
	print "IP Addr: "+instance.ip_address



def main():
	if args.instype == "spot":
		deploy_ec2_instances_spot(args.region) 
	elif args.instype == "demand":
		deploy_ec2_instances_demand(args.region)	

if  __name__ =='__main__':main()

