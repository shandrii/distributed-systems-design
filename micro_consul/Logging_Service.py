from flask import Flask, jsonify, abort, request
import json, argparse, hazelcast, subprocess
import consul, uuid
from os import getenv

def con_get_setts(sett):
	trash, setts = con_client.kv.get(sett)
	if setts:
		return json.loads(setts['Value'])
	else:
		raise Exception(f"The setting does not exist - {sett}.")


def con_create_serv_record(serv_name, serv_port):
	serv_ID = str(uuid.uuid4())
	serv_ip = getenv('SERVICE_IP', 'localhost')
	con_client.agent.service.register(serv_name, service_id=serv_ID, address=serv_ip, port=serv_port)
	return serv_ID


def con_delete_serv_record(ID):
	return con_client.agent.service.deregister(ID)

service_m = Flask(__name__)

messages = {}
messages['hz_messages'] = []

pars = argparse.ArgumentParser()
pars.add_argument("--hz_port", type=int, required=True) #hazelcast port
pars.add_argument("--ls_port", type=int, required=True) #logging servise port
pars.add_argument("--consul_addr", type=str, required=True) #consul addr
pars.add_argument("--consul_port", type=int, required=True) #consul port
args = pars.parse_args()
hz_port = args.hz_port
ls_port = args.ls_port
consul_addr = args.consul_addr
consul_port = args.consul_port

con_client = consul.Consul(host=consul_addr, port=consul_port)

subprocess.run(['sudo', 'docker', 'run', '-d', '--name', f'Node_{hz_port}', '-it', '--network', 'hazelcast-network', '--rm', '-e', f'HZ_NETWORK_PUBLICADDRESS=192.168.0.3:{hz_port}', '-e', 'HZ_CLUSTERNAME=hz_cluster', '-p', f'{hz_port}:5701', 'hazelcast/hazelcast:latest'])

hz_setts = con_get_setts('hazelcast_setts')
serv_ID = con_create_serv_record('Logging_Service', ls_port)
hz_client = hazelcast.HazelcastClient(cluster_name=hz_setts['cluster_name'])
hz_messages = hz_client.get_map(hz_setts['hz_map_name']).blocking()


@service_m.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "Method Not Allowed", "message": "Used method is forbidden for the selected URL address."}), 405 #Method Not Allowed

@service_m.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Bad Request", "message": error.description}), 400 #Bad Request


@service_m.route("/logging", methods=["POST", "GET"])
def logging_req():
    if request.method == "POST":
        _ID = request.form.get('id')
        _message = request.form.get('message')
        hz_messages.put(_ID, _message)
	
        if not (_ID):
            if not (_message):
                abort(400, "Fields 'id' and 'message' are empty in the POST request.")
            else:
                abort(400, "Field 'id' is empty in the POST request.")

        if not (_message):
            abort(400, "Field 'message' is empty in the POST request.")
            
        messages[_ID] = _message
        print("Received message:", _message)
        return "Message was successfully logged.", 201 #Created

    elif request.method == "GET":
    	#return jsonify(list(messages.values()))
    	messages['hz_messages'].clear()
    	hz_keys = hz_messages.key_set()
    	for key in hz_keys:
    	    messages['hz_messages'].append(hz_messages.get(key))
    	return messages

    else:
        abort(405) #Method Not Allowed

if __name__ == '__main__':
    service_m.run(port=ls_port)
    try:
    	while True:
    		pass
    except KeyboardInterrupt:
        hz_client.shutdown()
        con_delete_serv_record(serv_ID)
