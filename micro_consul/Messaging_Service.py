from flask import Flask
import argparse, hazelcast, json, uuid, os
from threading import Thread
import hazelcast, consul

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


def con_delete_serv_record(ID):
	return con_client.agent.service.deregister(ID)

service_m = Flask(__name__)

pars = argparse.ArgumentParser()
pars.add_argument("--ms_port", type=int, required=True) #messaging service port
pars.add_argument("--consul_addr", type=str, required=True) #consul port
pars.add_argument("--consul_port", type=int, required=True) #consul port
args = pars.parse_args()
ms_port = args.ms_port
consul_addr = args.consul_addr
consul_port = args.consul_port

con_client = consul.Consul(host=consul_addr, port=consul_port)

hz_setts = con_get_setts('hazelcast_setts')
serv_ID = con_create_serv_record('Messaging_Service', ms_port)
hz_client = hazelcast.HazelcastClient(cluster_name=hz_setts['cluster_name'])
hz_queue = hz_client.get_queue(hz_setts['hz_queue_name']).blocking()

messages = {}
messages['ms_messages'] = []

def proc_messages_queue():
	while True:
		try:
			_message = hz_queue.take()
			print("Got message: " + _message)
			messages['ms_messages'].append(_message)
			if (_message == -1):
				hz_queue.put(-1)
				break
		except:
			hz_client.shutdown()
			con_delete_serv_record(serv_ID)
			exit()
	
	
@service_m.route('/messaging', methods=['GET'])
def get_messages():
	print(messages)
	return messages

if __name__ == '__main__':
	thread_cycle = Thread(target=proc_messages_queue)
	thread_cycle.start()
	service_m.run(port=ms_port)
	
	try:
		service_m.run(port=ms_port)
		thread_cycle.join()
	except KeyboardInterrupt:
		hz_client.shutdown()
		con_delete_serv_record(serv_ID)
		exit()
