import uuid, requests, socket, random, json
from flask import Flask, jsonify, abort, request
import hazelcast


logging_serv_ports = [4447, 4448, 4449]
messaging_serv_ports = [4445, 4446]
messages=[]


hz_client = hazelcast.HazelcastClient(cluster_name="hz_cluster")
hz_queue = hz_client.get_queue("hz_queue").blocking()

service_m = Flask(__name__)

@service_m.route("/", methods=["POST", "GET"])
def process_req():
    if request.method == "POST":
        _message = request.form.get("message")
        if not _message:
            return "Message field is empty. Status code 400.", 400 #Bad Request

        _ID = str(uuid.uuid4())
        info = {"id": _ID, "message": _message}
	
        logging = "http://127.0.0.1:{}/logging".format(random.choice(logging_serv_ports))
        response = requests.post(logging, data=info)
        hz_queue.offer(json.dumps(_message))

        return jsonify(info), 200 #OK

    elif request.method == "GET":
        logging = "http://127.0.0.1:{}/logging".format(random.choice(logging_serv_ports))
        messaging = "http://127.0.0.1:{}/messaging".format(random.choice(messaging_serv_ports))
        
        logging_resp = requests.get(logging)
        messaging_resp = requests.get(messaging)
        if messaging_resp.text not in messages:
        	messages.append(str(messaging_resp.text))
        return jsonify([logging_resp.text, str(messages)]), 200

    else:
        abort(400) #Bad Request

if __name__ == "__main__":
    service_m.run(port=4444)
