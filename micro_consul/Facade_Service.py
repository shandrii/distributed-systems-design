import uuid, requests, json, argparse, os
from flask import Flask, jsonify, abort, request
import hazelcast, consul
from random import randint

def con_create_serv_record(serv_name, serv_port):
	serv_ID = str(uuid.uuid4())
	serv_ip = os.getenv('SERVICE_IP', 'localhost')
	con_client.agent.service.register(serv_name, service_id=serv_ID, address=serv_ip, port=serv_port)
	return serv_ID


def con_get_setts(sett):
	trash, setts = con_client.kv.get(sett)
	if setts:
		return json.loads(setts['Value'])
	else:
		raise Exception(f"The setting does not exist - {sett}.")

def con_get_serv_address(serv_name):
	trash, servs = con_client.catalog.service(serv_name)
	serv = randint(0, len(servs) - 1)
	if servs:
		addr = servs[serv]['ServiceAddress']
		port = servs[serv]['ServicePort']
		URL = f"http://{addr}:{port}"
		return URL
	else:
		raise Exception(f"The service does not exist - {serv_name}.")

def con_delete_serv_record(ID):
	return con_client.agent.service.deregister(ID)
	
pars = argparse.ArgumentParser()
pars.add_argument("--fs_port", type=int, required=True) #facade service port
pars.add_argument("--consul_addr", type=str, required=True) #consul addr
pars.add_argument("--consul_port", type=int, required=True) #consul port
args = pars.parse_args()
fs_port = args.fs_port
consul_addr = args.consul_addr
consul_port = args.consul_port

messages=[]

con_client = consul.Consul(host=consul_addr, port=consul_port)

def system_shutdown(hz_client, serv_ID):
    hz_client.shutdown()
    con_delete_serv_record(serv_ID)

serv_ID = con_create_serv_record('Facade_Service', fs_port)
hz_setts = con_get_setts('hazelcast_setts')
hz_client = hazelcast.HazelcastClient(cluster_name=hz_setts['cluster_name'])
hz_queue = hz_client.get_queue(hz_setts['hz_queue_name']).blocking()

service_m = Flask(__name__)

@service_m.route("/", methods=["POST", "GET"])
def process_req():
    if request.method == "POST":
        _message = request.form.get("message")
        if not _message:
            return "Message field is empty. Status code 400.", 400 #Bad Request

        _ID = str(uuid.uuid4())
        info = {"id": _ID, "message": _message}
	
        logging = f"{con_get_serv_address('Logging_Service')}/logging"
        response = requests.post(logging, data=info)
        hz_queue.offer(json.dumps(_message))

        return jsonify(info), 200 #OK

    elif request.method == "GET":
        logging = f"{con_get_serv_address('Logging_Service')}/logging"
        messaging = f"{con_get_serv_address('Messaging_Service')}/messaging"
        
        logging_resp = requests.get(logging)
        messaging_resp = requests.get(messaging)
        if messaging_resp.text not in messages:
        	messages.append(str(messaging_resp.text))
        	
        return jsonify([logging_resp.text, str(messages)]), 200

    else:
        abort(400) #Bad Request

if __name__ == "__main__":
    service_m.run(port=fs_port)
    
    try:
    	while True:
    		pass
    except KeyboardInterrupt:
    	system_shutdown(hz_client, serv_ID)
