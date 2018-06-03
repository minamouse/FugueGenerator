'''Make one-hot versions of the data'''
import numpy as np

def populate_pitch_values():

	pitch_values = []
	pitch_classes = ['C', 'C#', 'D', 'E-', 'E', 'F', 'F#', 'G', 'G#', 'A', 'B-', 'B']
	for i in range(0, 127):
		note_name = pitch_classes[i % 12]
		# register = i/12 - 1
		register = (i + 12 // 2) // 12
		pitch_values.append(note_name+str(register))
	pitch_values.append('R')
	pitch_values.append('_')
	pitch_values.append('fin')
	return pitch_values

pitch_values = populate_pitch_values()

def make_one_hot_vector_X(X, m, Tx, pitch_values):

	Xoh = np.zeros((m, Tx, len(pitch_values)))
	for i in range(m):
		for j in range(Tx):
			note = X[i][j]
			ind = pitch_values.index(note)
			one_hot = np.zeros((len(pitch_values)))
			one_hot[ind] = 1
			Xoh[i][j] = one_hot
	return Xoh

def make_one_hot_vector_Y(Y, m, Ty, n_c_Y, pitch_values):

	Yoh = np.zeros((m, Ty, n_c_Y-1, len(pitch_values)))
	Y = Y[:][:][0:n_c_Y-1]
	for i in range(m):
		for j in range(Ty):
			all_one_hots = np.zeros((n_c_Y-1, len(pitch_values)))
			for k in range(n_c_Y-1):
				note = Y[i][j][k]
				ind = pitch_values.index(note)
				one_hot = np.zeros((len(pitch_values)))
				one_hot[ind] = 1
				all_one_hots[k,:] = one_hot
			Yoh[i][j] = all_one_hots
	return Yoh

def make_X_numpy_array(X):
	m = len(X)
	Tx = len(X[0])
	X_np = np.zeros((m, Tx))
	pitch_values = populate_pitch_values()
	for i in range(m):
		for j in range(Tx):
			X_np[i][j] = pitch_values.index(X[i][j])
	return X_np

def make_Y_numpy_array(Y):
	m = len(Y)
	Ty = len(Y[0])
	n_c_Y = len(Y[0][0])
	Y_np = np.zeros((m, Ty, n_c_Y-1))
	pitch_values = populate_pitch_values()
	for i in range(m):
		for j in range(Ty):
			for k in range(n_c_Y-1):
				Y_np[i][j][k] = pitch_values.index(Y[i][j][k])
	return Y_np



