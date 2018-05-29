'''DEEPFUGUE MODEL VER 1
MAY 28 2018
ADITYA CHANDER
SAMANTHA SILVERSTEIN
MARINA COTTRELL
Based on Neural Machine Translation assignment from Coursera – NLP/Sequence Models'''

from keras.models import Model
from keras.layers import Input, LSTM, Dense, Activation, Dropout, Reshape, Lambda, RepeatVector, Concatenate, Dot
from keras.optimizers import Adam
import numpy as np
from music21 import midi

# Dimensions of arrays
Tx = None
Ty = None
m = None
n_c_Y = 5
n_pitches = 131 # number of MIDI pitches + rest token + sustain token + fin token

# Hyperparameters
batch_size = 4
epochs = 10
n_units_densor1 = 10
n_units_densor2 = 1
n_a = 32 # hidden state size of bidirectional LSTM
n_s = 64 # hidden state size of post-attention LSTM

# Placeholders for data
X = np.zeros((m, Tx))
Y = np.zeros((m, Ty, n_c_Y))
Xoh = np.zeros((m, Tx, n_pitches)) # ignoring subdivision information for now
Yoh = np.zeros((m, Ty, n_c_Y-1, n_pitches))

print('Number of timesteps in subjects: ', Tx)
print('Number of timesteps in fugues: ', Ty)
print('Number of training examples: ', m)

# Define shared layers as global variables
repeator = RepeatVector(Tx)
concatenator = Concatenate(axis=-1)
densor1 = Dense(n_units_densor1, activation="tanh")
densor2 = Dense(n_units_densor2, activation="relu")
activator = Activation(softmax(axis = 1), name="attention_weights")
dotor = Dot(axes = 1)

# Output layers
post_activation_LSTM_cell = LSTM(n_s, return_state = True)
output_layer_1 = Dense(len(n_pitches), activation=softmax)
output_layer_2 = Dense(len(n_pitches), activation=softmax)
output_layer_3 = Dense(len(n_pitches), activation=softmax)
output_layer_4 = Dense(len(n_pitches), activation=softmax)

# One step of attention weights computation. Get a context vector for a particular time step
def one_step_attention(a, s_prev):
	s_prev = repeator(s_prev)
	concat = concatenator([a, s_prev])
	e = densor1(concat)
	energies = densor2(e)
	alphas = activator(energies)
	context = dotor([alphas, a])
	return context

'''
Tx: max fugue subject length
Ty: max fugue length
n_a, n_s: as above
n_pitches: size of pitch "vocabulary" for both input and output. Excluding beat information.

Return: Keras model instance
'''
def model(Tx, Ty, n_a, n_s, n_pitches):
	X = Input(shape=(Tx, n_pitches))
	s0 = Input(shape=(n_s, ), name='s0')
	c0 = Input(shape=(n_s, ), name='c0')
	s = s0
	c = c0 # to initialise for looping

	outputs = []

	a = Bidirectional(LSTM(n_a, return_sequences=True))(X)
    print(a.shape)
    
    for t in range(Ty):
        context = one_step_attention(a,s)
        s, _, c = post_activation_LSTM_cell(context, initial_state=[s,c])
        out = output_layer(s)
        outputs.append(out)

    model = Model(inputs=[X, s0, c0], outputs=outputs)

    return model

model = model(Tx, Ty, n_a, n_s, n_pitches)

model.summary()

opt = Adam(lr=0.005, beta_1=0.9, beta_2=0.999, decay=0.01)
model.compile(loss='categorical_crossentropy', optimizer=opt, metrics=['accuracy'])

s0 = np.zeros((m, n_s))
c0 = np.zeros((m, n_s))
outputs = list(Yoh.swapaxes(0,1))

model.fit([Xoh, s0, c0], outputs, epochs=1, batch_size=100)