import tensorflow as tf
import numpy as np
import config
import cv2

def load_graph(frozen_graph_filename):
    # We load the protobuf file from the disk and parse it to retrieve the 
    # unserialized graph_def
    with tf.gfile.GFile(frozen_graph_filename, "rb") as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())

    # Then, we import the graph_def into a new Graph and returns it 
    with tf.Graph().as_default() as graph:
        # The name var will prefix every op/nodes in your graph
        # Since we load everything in a new graph, this is not needed
        tf.import_graph_def(graph_def, name="model")
    return graph

graph = load_graph(config.model_path)

for op in graph.get_operations():
    print(op.name)
# Get the input and embedding tensors of the network 
phase_train_placeholder = graph.get_tensor_by_name('model/phase_train:0')
image = graph.get_tensor_by_name('model/input:0')
embedding = graph.get_tensor_by_name('model/embeddings:0')

def preprocess_image(image_path):
    """ Load the image, resize and normalized it
    Note: The way we normalize the image here should be
    consistant with the way we nomalize the images while training
    """
    img = cv2.imread(image_path)
    img_resized = cv2.resize(img,(160, 160))
    img_resized = np.expand_dims(img_resized, axis=0).astype(float)
    img_resized = (img_resized - 127.5) / 128.0
    return img_resized

def get_embedding(image_path):
    """ Helper function to get an embedding of a image
    Load and pre-process the image
    Feed the image into the network and get the embedding vector
    """

    img = preprocess_image(image_path)

    with tf.Session(graph=graph) as sess:
        emb = sess.run(embedding, feed_dict={image: img, phase_train_placeholder: False})
        return emb.squeeze()

# test_img = './images/1598697513.6673055.jpg'
# test_eb = get_embedding(test_img)
# print(test_eb.shape)