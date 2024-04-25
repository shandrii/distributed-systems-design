from flask import Flask
import argparse, hazelcast
from threading import Thread

service_m = Flask(__name__)

pars = argparse.ArgumentParser()
pars.add_argument("--ms_port", type=int, required=True) #messaging service port
args = pars.parse_args()
ms_port = args.ms_port

hz_client = hazelcast.HazelcastClient(cluster_name="hz_cluster")
hz_queue = hz_client.get_queue("hz_queue").blocking()

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
			exit()
	
	
@service_m.route('/messaging', methods=['GET'])
def get_messages():
	print(messages)
	return messages

if __name__ == '__main__':
	thread_cycle = Thread(target=proc_messages_queue)
	thread_cycle.start()
	service_m.run(port=ms_port)
