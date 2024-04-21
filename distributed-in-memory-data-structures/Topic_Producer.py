import hazelcast
from time import sleep

if __name__ == "__main__":
	hz_client = hazelcast.HazelcastClient(cluster_name="hz_cluster")
	hz_topic = hz_client.get_topic("t_topic").blocking()
	
	
	for i in range(100): 
		hz_topic.publish("The objective number " + str(i) + " was published in topic.")
		sleep(1)
