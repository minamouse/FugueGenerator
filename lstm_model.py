from keras.models import Model
from keras.layers import Input, LSTM, Dense, Activation, Dropout, Reshape, Lambda, RepeatVector
from keras.optimizers import Adam
import numpy as np
from music21 import midi

Tx = None
m = None
n_c = 5
