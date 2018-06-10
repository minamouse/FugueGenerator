#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''DEEPFUGUE MODEL VER 1
MAY 28 2018
ADITYA CHANDER
SAMANTHA SILVERSTEIN
MARINA COTTRELL
Based on Neural Machine Translation assignment from Coursera – NLP/Sequence Models'''

from keras.models import Model, load_model
from keras.layers import Input, LSTM, Dense, Bidirectional, Activation, Dropout, Reshape, Lambda, RepeatVector, Concatenate, Dot, Softmax
from keras.optimizers import Adam
import numpy as np
from music21 import midi
import pickle
# from process_files import *

# Load in the data
def load_data(path):
    file = open(path, 'rb')
    dataset = pickle.load(file, encoding='latin1')
    X = dataset['X']
    Y = dataset['Y']
    Xoh = dataset['Xoh']
    Yoh = dataset['Yoh']
    Tx = X.shape[1]
    Ty = Y.shape[1]
    m = X.shape[0]
    return Xoh, Yoh, Tx, Ty, m

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
def the_model(Tx, Ty, n_a, n_s, n_pitches):
    X = Input(shape=(Tx, n_pitches))
    s0 = Input(shape=(n_s, ), name='s0')
    c0 = Input(shape=(n_s, ), name='c0')
    s = s0
    c = c0 # to initialize for looping

    outputs = []

    a = Bidirectional(LSTM(n_a, return_sequences=True))(X)
    print("Running the_model with", Ty)
    
    for t in range(Ty):
        # if t % (Ty / 20) == 0:
        print("At iteration ", t, "/", Ty)
        context = one_step_attention(a,s)
        s, _, c = post_activation_LSTM_cell(context, initial_state=[s,c])
        outputs.append(output_layer(s))

    model = Model(inputs=[X, s0, c0], outputs=outputs)

    return model


if __name__ == '__main__':

    Xoh, Yoh, Tx, Ty, m = load_data('datasets/fugues.p')
    # Dimensions of arrays
    n_c_Y = 5
    n_pitches = 131 # number of MIDI pitches + rest token + sustain token + fin token

    # Hyperparameters
    batch_size = 32
    epochs = 100
    n_units_densor1 = 10
    n_units_densor2 = 1
    n_a = 64 # hidden state size of bidirectional LSTM
    n_s = 128 # hidden state size of post-attention LSTM

    # Placeholders for data
    X = np.zeros((m, Tx))
    Y = np.zeros((m, Ty, n_c_Y))

    # Define shared layers as global variables
    repeator = RepeatVector(Tx)
    concatenator = Concatenate(axis=-1)
    densor1 = Dense(n_units_densor1, activation="tanh")
    densor2 = Dense(n_units_densor2, activation="relu")
	# I think you can delete the line below, it causes warnings and the activator is never used........
    activator = Activation('softmax', name="attention_weights") # UserWarning: Do not pass a layer instance (such as Softmax) as the activation argument of another layer. Instead, advanced activation layers should be used just like any other layer in a model.
    dotor = Dot(axes = 1)

    # Output layers
    post_activation_LSTM_cell = LSTM(n_s, return_state = True)
    output_layer = Dense(n_pitches, activation='softmax')
    print("A")

    model = the_model(Tx, Ty, n_a, n_s, n_pitches)
    print("B")

    model.summary()
    print("C")

    opt = Adam(lr=0.005, beta_1=0.9, beta_2=0.999, decay=0.01)
    model.compile(loss='categorical_crossentropy', optimizer=opt, metrics=['accuracy'])
    print("D")

    s0 = np.zeros((m, n_s))
    c0 = np.zeros((m, n_s))
    outputs = list(Yoh.swapaxes(0,1))

    print("E")
    model.fit([Xoh, s0, c0], outputs, epochs=100, batch_size=32, verbose=1)

    print("F")
    model.save('fugue_model5.h5')
    print("G")

