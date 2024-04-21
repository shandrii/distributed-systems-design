import hazelcast


if __name__ == "__main__":
	hz_client = hazelcast.HazelcastClient(cluster_name="hz_cluster")
	hz_queue = hz_client.get_queue("t_queue").blocking() 
	
	while True:
		item = hz_queue.take()
		print("Item number " + str(item) + " was consumed.")
		if (item == -1):
			hz_queue.put(-1)
			break
