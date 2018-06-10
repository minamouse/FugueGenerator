import numpy as np
from keras.models import load_model
import pickle

def make_one_hot_vector(X, m, Tx):

    Xoh = np.zeros((m, Tx, 131))
    for i in range(m):
        for j in range(Tx):
            note = X[i][j]
            one_hot = np.zeros(131)
            one_hot[int(note)] = 1
            Xoh[i][j] = one_hot
    return Xoh


def make_X_numpy_array(X):
    m = len(X)
    Tx = len(X[0])
    X_np = np.zeros((m, Tx))
    for i in range(m):
        for j in range(Tx):
            X_np[i][j] = X[i][j]
    return X_np

def predict():

#    twinkle = [60, 129, 129, 129,
#	           60, 129, 129, 129,
#			   67, 129, 129, 129,
#			   67, 129, 129, 129,
#			   69, 129, 129, 129,
#			   69, 129, 129, 129,
#			   67, 129, 129, 129, 129, 129, 129, 129,
#			   65, 129, 129, 129,
#			   65, 129, 129, 129,
#			   64, 129, 129, 129,
#			   64, 129, 129, 129,
#			   62, 129, 129, 129,
#			   62, 129, 129, 129,
#			   60, 129, 129, 129, 129, 129, 129, 129,
#			   130]
    twinkle = [60, 129, 129, 129, 67, 129, 129, 129, 69, 129, 129, 129, 67, 129, 129, 129, 129, 129, 129, 129, 130]
    twinkle = make_X_numpy_array([twinkle])
    twinkle = make_one_hot_vector(twinkle, len(twinkle), len(twinkle[0]))
    #model = load_model('fugue_model.h5')
    #prediction = model.predict(twinkle)
    #return prediction
    return twinkle


#def get_indices(prediction):
#    
#	indices = []
#    for p in prediction:
#        indices.append(p.index(max(p)))

#	return indices


#def split_parts(indices):
	
#	l = len(indices)
#	s, a, t, b = indices[:l/4], indices[l/4:l/2], indices[l/2:l-(l/4)]. indices[l-(l/4):]
#	return s, a, t, b


#def make_voice(voice):
	

 #   return


model = load_model('fugue_model4.h5')
test = predict()
m = 96
n_s = 128
s0 = np.zeros((m, n_s))
c0 = np.zeros((m, n_s))
prediction = model.predict([test, s0, c0])
pickle.dump(prediction, open('prediction5.p', 'wb'))