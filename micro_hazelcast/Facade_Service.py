import uuid, requests, socket, random
from flask import Flask, jsonify, abort, request


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
messaging = "http://127.0.0.1:4445/messaging"
logging_serv_ports = [4446, 4447, 4448]

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

        return jsonify(info), 200 #OK

    elif request.method == "GET":
        logging = "http://127.0.0.1:{}/logging".format(random.choice(logging_serv_ports))
        logging_resp = requests.get(logging)
        messaging_resp = requests.get(messaging)
        return jsonify([logging_resp.text, messaging_resp.text]), 200

    else:
        abort(400) #Bad Request

if __name__ == "__main__":
    service_m.run(port=4444)
