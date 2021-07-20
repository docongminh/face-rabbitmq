import numpy as np
import mxnet as mx
import sklearn

class ExtractModel:
	def __init__(self, config):
		self.ctx = mx.cpu()
		self.layer = config["layer"] #fc1"
		self.prefix = config["prefix"] #"/models/mobilefacenet/model"
		self.epoch = config["epoch"] #0
		self.image_size = config["image_size"] #112
		self.model = self.get_model()

	def get_model(self):
		"""
			
		"""
		print('loading', self.prefix, self.epoch)
		sym, arg_params, aux_params = mx.model.load_checkpoint(self.prefix, self.epoch)
		all_layers = sym.get_internals()
		sym = all_layers[self.layer+'_output']
		model = mx.mod.Module(symbol=sym, context=self.ctx, label_names = None)
		model.bind(data_shapes=[('data', (1, 3, self.image_size, self.image_size))])
		model.set_params(arg_params, aux_params)
		return model

	def extract_feature(self, faces_aligned):
		input_blob = np.expand_dims(faces_aligned, axis=0)
		print(input_blob.shape)
		data = mx.nd.array(input_blob)
		db = mx.io.DataBatch(data=(data,))
		self.model.forward(db, is_train=False)
		output = self.model.get_outputs()
		embedding = output[0].asnumpy()
		embedding = sklearn.preprocessing.normalize(embedding).flatten()
		return embedding