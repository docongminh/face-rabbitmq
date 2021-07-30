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

host = None
search_service = {
    "milvus_config": {
        # https://stackoverflow.com/questions/24319662/from-inside-of-a-docker-container-how-do-i-connect-to-the-localhost-of-the-mach
        "host": host, # this is why use ip address rather than localhost: https://docs.docker.com/docker-for-mac/networking/#vpn-passthrough
        "port": 19530,
        "embedding_size": 128,
        "collection_name": "Face_Embedding",
        "metric": "L2"
    },
    "rabbitmq_config": {
        "durable": True,
        "exchange_name": "face_service",
        "exchange_type": "direct",
        "binding_key": "search",
        "queue_name": "SEARCH"
    },
    "publisher_config": {
        "exchange_name": "face_service",
        "routing_key": "response"
    }
}