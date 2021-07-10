import numpy as np

def face_distance(face_encodings, face_to_compare):
	if len(face_encodings) == 0:
		return np.empty((0))
	face_dist_value = np.linalg.norm(face_encodings - face_to_compare, axis=1)
	print('[Face Services | face_distance] Distance between two faces is {}'.format(
		face_dist_value))
	return face_dist_value
