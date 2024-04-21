import hazelcast

if __name__ == "__main__":
	
	hz_client = hazelcast.HazelcastClient(cluster_name="hz_cluster")
	map = hz_client.get_map("Distributed_Map_Demo").blocking()
	
	for k in range(0, 1000): map.put(k, k)
