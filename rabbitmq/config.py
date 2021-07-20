admin = {
		"host": "192.168.82.111",
		"username": "guest",
		"password": "guest",
		"vhost": "/",
		"port": "5672"
}

broker = {
		"exchange_name": "face_service",
		"exchange_type": "direct",
		"detect_queue": "Q_DETECTION",
		"extract_queue": "Q_EXTRACT",
		"match_face_queue": "Q_MATCHING",
		"response_queue": "Q_RESPONSE"
}
routing_keys = {
		"detect_key": "detect",
		"extract_key": "extract",
		"match_face_key": "matching",
		"response_key": "response"
}