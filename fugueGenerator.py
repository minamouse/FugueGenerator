# MAIN FUNCTION #
import pickle
from lstm_model import *
import numpy as np
from keras.models import Model
from keras.optimizers import 

Tx = None
Ty = None
m = None
n_pitches = 131

# Hyperparameters
n_a = 32 # hidden state size of bidirectional LSTM
n_s = 64 # hidden state size of post-attention LSTM

model = model(Tx, Ty, n_a, n_s, n_pitches)

model.summary()

opt = Adam(lr=0.005, beta_1=0.9, beta_2=0.999, decay=0.01)
model.compile(loss='categorical_crossentropy', optimizer=opt, metrics=['accuracy'])

s0 = np.zeros((m, n_s))
c0 = np.zeros((m, n_s))
outputs = list(Yoh.swapaxes(0,1))

model.fit([Xoh, s0, c0], outputs, epochs=1, batch_size=100)

def load_all_variables():
