# model_config = {
#     "detect": {
#         "mtcnn_model": {
#             "prefix":
#             "epoch":
#             "image_size":
#             "threshold":
#             "det_minsize":
#         },
#         "retina_face": ""
#     },
#     "recognition": {
#         "arcface_mxnet": ""
#     }
# }

rabbit_config = {
    "host": "10.1.16.148",
    "port": 5672,
    "username": "admin",
    "password": "123456",
}

redis_config = {
    "host": "localhost",
    "port": 6379,
    "db": 0,
}

queue_config = {
    "q_identify_name": "Q_EXTRACT_FEATURE",
}

mongo_config = {
    "uri": "mongodb://127.0.0.1:27017/",
    "database_name": "f-vision-saas",
    "face_table": "faces",
}

input_nodes = ['img_inputs:0', 'dropout_rate:0']
output_nodes = ['resnet_v1_50/E_BN2/Identity:0']
device = '/cpu:0'
model_frozen = '/models/insightface.pb'
model_path = '/models/model_ir_se50.pth'
image_shape = (112, 112)
dropout = 1.0
store_config = {
    "store_dir": "/stores/images",
    "store_url": "http://stores.seventofive.io/images",
}

threshold = 30
