from flask import Flask, jsonify, abort, request
import json, argparse, hazelcast, subprocess

service_m = Flask(__name__)
messages = {}

messages_array = {}
messages_array['hz_messages'] = []

pars = argparse.ArgumentParser()
pars.add_argument("--hz_port", type=int, required=True) #hazelcast port
pars.add_argument("--ls_port", type=int, required=True) #logging servise port
args = pars.parse_args()
hz_port = args.hz_port
ls_port = args.ls_port

subprocess.run(['sudo', 'docker', 'run', '-d', '--name', f'Node_{hz_port}', '-it', '--network', 'hazelcast-network', '--rm', '-e', f'HZ_NETWORK_PUBLICADDRESS=192.168.0.3:{hz_port}', '-e', 'HZ_CLUSTERNAME=hz_cluster', '-p', f'{hz_port}:5701', 'hazelcast/hazelcast:latest'])

hz_client = hazelcast.HazelcastClient(cluster_name="hz_cluster")
hz_messages = hz_client.get_map("hz_map_messages").blocking()

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
    	messages_array['hz_messages'].clear()
    	hz_keys = hz_messages.key_set()
    	for key in hz_keys:
    	    messages_array['hz_messages'].append(hz_messages.get(key))
    	return messages_array

    else:
        abort(405) #Method Not Allowed

if __name__ == '__main__':
    service_m.run(port=ls_port)
