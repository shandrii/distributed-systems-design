from flask import Flask, jsonify, abort, request
import json

service_m = Flask(__name__)
messages = {}

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
    	return jsonify(list(messages.values()))

    else:
        abort(405) #Method Not Allowed

if __name__ == '__main__':
    service_m.run(port=4445)
