import hazelcast

hz_client = hazelcast.HazelcastClient(cluster_name="hz_cluster")
hz_queue = hz_client.get_queue("t_queue").blocking() 

if __name__ == "__main__":
	for i in range(100):
		hz_queue.put(i)
		print("Item number " + str(i) + " was produced.")
		
	hz_queue.put(-1)
	print("100 items were produced.")
	hz_client.shutdown()
