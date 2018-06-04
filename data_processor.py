import os
from music21 import converter, note
import numpy as np
import pickle


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


def get_file_names(path):
    """Iterate through subfolders of given path and find all the file names within"""
    names = []
    for f in os.listdir(path):
        new_path = os.path.join(path, f)
        if os.path.isfile(new_path):
            names.append(new_path)
        elif os.path.isdir(new_path):
            names.extend(get_file_names(new_path))

    return names


def filter_file_list(file_list):
    """Validates files based on number of voices and whether or not music21 will parse it."""
    l = []
    for file_name in file_list:
        try:
            c = converter.parse(file_name)
            if len(c.parts) == num_voices:
                l.append(file_name)
            else:
                print(file_name, "wrong number of voices")
        except:
            print(file_name, "won't parse")
    return l


def make_time_stamp(length):
    time = [1,2,3,4]
    time_stamp = []
    for i in range(int(length/4)):
        time_stamp.extend(time)

    for i in range(length % 4):
        time_stamp.append(time[i])

    return time_stamp


def get_subject(piece, active_voices):

    summed = [sum(l) for l in zip(*active_voices)]
    if summed[0] <= 1:
        voice_num = 0
        for n, voice in enumerate(piece[:4]):
            if voice[0] != 'R':
                voice_num = n
        ind = summed.index(2)
        return piece[voice_num][:ind]


def process_voice(piece, part):

    entire_part = []
    try:
        for n in piece.parts[part].flat:
            if isinstance(n, note.Note):
                entire_part.append([n.nameWithOctave, n.duration.quarterLength])
            elif isinstance(n, note.Rest):
                entire_part.append(['R', n.duration.quarterLength])
    except (AttributeError, IndexError):
        pass

    return entire_part


def expand_part(part):

    new_part = []
    active_voices = []

    for p in part:
        new_part.append(p[0])
        if p[0] == 'R':
            active_voices.append(0)
            for i in range(int(p[1]/step)-1):
                active_voices.append(0)
        else:
            active_voices.append(1)
            for i in range(int(p[1]/step)-1):
                active_voices.append(1)
        for i in range(int(p[1]/step)-1):
            new_part.append('_')
    return new_part, active_voices


def process_piece(chorale):

    chorale = converter.parse(chorale)
    parts = []
    for part in range(num_voices):
        parts.append(process_voice(chorale, part))

    new_parts = []
    active_voices = []
    for part in parts:
        new_part, active_voice = expand_part(part)
        new_parts.append(new_part)
        active_voices.append(active_voice)

    lengths = [len(p) for p in new_parts]
    if all(l == lengths[0] for l in lengths):
        return new_parts, active_voices
    return None, None


def process_pieces(pieces):

    new_pieces = []
    active_voices = []

    for piece in pieces:
        new_piece, active_voice = process_piece(piece)
        if new_piece:
            new_pieces.append(new_piece)
            active_voices.append(active_voice)
        else:
            print(piece, "uneven voice lengths")

    return new_pieces, active_voices


def make_subject_same_size(data, token='fin'):

    length = 0
    for d in data:
        if len(d) > length:
            length = len(d)


    length += 1
    new_data = []
    for d in data:
        while len(d) < length:
            d.append(token)
        new_data.append(d)

    return new_data


def make_fugues_same_size(data, token='fin'):

    length = 0
    for d in data:
        if len(d) > length:
            length = len(d)


    length += 1
    new_data = []
    for d in data:
        while len(d) < length:
            d.append((token, token, token, token, token))
        new_data.append(d)

    return new_data


def make_dataset(pieces, active_voices):

    X = []
    Y = []

    new_pieces = []
    for n, piece in enumerate(pieces):
        time_stamp = make_time_stamp(len(piece[0]))
        piece.append(time_stamp)
        new_pieces.append(piece)
        subject = get_subject(piece, active_voices[n])
        X.append(subject)
        Y.append(zip(*piece))

    X = make_subject_same_size(X)
    Y = make_fugues_same_size(Y)
    return {'X': X, 'Y': Y}


def return_data(dataset):
    X = make_X_numpy_array(dataset["X"])
    Y = make_Y_numpy_array(dataset["Y"])
    Xoh = make_one_hot_vector_X(dataset["X"], len(dataset["X"]), len(dataset["X"][0]), populate_pitch_values())
    Yoh = make_one_hot_vector_Y(dataset["Y"], len(dataset["Y"]), len(dataset["Y"][0]), len(dataset["Y"][0][0]), populate_pitch_values())
    return X, Y, Xoh, Yoh


if __name__ == '__main__':
    num_voices = 4
    step = 0.25
    files = get_file_names("fugueData/test")
    fugue_list = filter_file_list(files)
    fugues, active_voices = process_pieces(fugue_list)
    dataset = make_dataset(fugues, active_voices)
    print(dataset)
    X, Y, Xoh, Yoh = return_data(dataset)
    final_dataset = {}
    final_dataset['X'] = X
    final_dataset['Y'] = Y
    final_dataset['Xoh'] = Xoh
    final_dataset['Yoh'] = Yoh
    pickle.dump(final_dataset, open("datasets/fugues.p", "wb"))

