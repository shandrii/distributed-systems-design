import hazelcast, datetime

def event_trig(event):
	print("=================================================================")
	print("Publish time:", datetime.datetime.fromtimestamp(event.publish_time))
	print("The event:", event.message)
	print("=================================================================")
		
if __name__ == "__main__":	
	hz_client = hazelcast.HazelcastClient(cluster_name="hz_cluster")
	hz_topic = hz_client.get_topic("t_topic").blocking()
	
	hz_topic.add_listener(event_trig)
	
	try:
		while True:
			pass
	except KeyboardInterrupt: 
		hz_client.shutdown()
		print("KeyboardInterrupt was triggered.")
