from flask import Flask

service_m = Flask(__name__)

@service_m.route('/messaging', methods=['GET'])
def get_messages():
    return "Return of test get_messages() function."

if __name__ == '__main__':
    service_m.run(port=4446)
