#This script is to check whether we have killed instances when we're supposed to. It should run every hour.
import argparse
import boto.ec2
import sys
import argparse
import time

parser = argparse.ArgumentParser()
parser.add_argument("farmname")
args = parser.parse_args()


conn = boto.ec2.connect_to_region("eu-west-1")

reservations = conn.get_all_instances(filters={"tag:Farm" : args.farmname})
instances = [i for r in reservations for i in r.instances]
for instance in instances:
	conn.terminate_instances(instance.id)
