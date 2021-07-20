detect_service = {
    "model_config": {
        "det_threshold": [0.6,0.7,0.8],
        "image_size": [112, 112],
        "mtcnn_path": "/models/mtcnn-model"
    },
    "rabbitmq_config": {
        "durable": True, #https://github.com/MassTransit/MassTransit/issues/370
        "exchange_name": "face_service",
		"exchange_type": "direct",
        "binding_key": "detect",
		"queue_name": "DETECTION"
    },
    "publisher_config": {
        "exchange_name": "face_service",
		"routing_key": "extract"
    }

}

extract_service = {
    "model_config": {
        "layer": "fc1",
        "image_size": 112,
        "epoch": 0,
        "prefix": "/models/mobilefacenet/model"
    },
    "rabbitmq_config": {
        "durable": True,
        "exchange_name": "face_service",
		"exchange_type": "direct",
        "binding_key": "extract",
		"queue_name": "EXTRACTION"
    },
    "publisher_config": {
        "exchange_name": "face_service",
		"routing_key": "response"
    }
}