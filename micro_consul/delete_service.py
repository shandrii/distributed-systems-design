import argparse, consul

def con_delete_serv_record(ID):
	return con_client.agent.service.deregister(ID)
	
pars = argparse.ArgumentParser()
pars.add_argument("--serv_id", type=str, required=True) #facade service port
args = pars.parse_args()
serv_id = args.serv_id

con_client = consul.Consul(host="127.0.0.1", port=8500)

if __name__ == "__main__":
	con_delete_serv_record(serv_id)
