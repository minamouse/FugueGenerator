import os
from music21 import converter, note
import numpy as np
import pickle
from pprint import pprint as pp


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


def make_Y_numpy_array(Y):
    m = len(Y)
    Ty = len(Y[0])
    n_c_Y = len(Y[0][0])
    Y_np = np.zeros((m, Ty * (n_c_Y-1)))
    for i in range(m):
        for j in range(Ty):
            for k in range(n_c_Y-1):
                Y_np[i][j+(k*Ty)] = Y[i][j][k]
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
            if voice[0] != 128:
                voice_num = n
        ind = summed.index(2)
        return piece[voice_num][:ind]


def process_voice(piece, part):

    entire_part = []
    try:
        for n in piece.parts[part].flat:
            if isinstance(n, note.Note):
                entire_part.append([n.pitch.midi, n.duration.quarterLength])
            elif isinstance(n, note.Rest):
                entire_part.append([128, n.duration.quarterLength])
    except (AttributeError, IndexError):
        pass

    return entire_part


def expand_part(part):

    new_part = []
    active_voices = []

    for p in part:
        new_part.append(p[0])
        if p[0] == 128:
            active_voices.append(0)
            for i in range(int(p[1]/step)-1):
                active_voices.append(0)
        else:
            active_voices.append(1)
            for i in range(int(p[1]/step)-1):
                active_voices.append(1)
        for i in range(int(p[1]/step)-1):
            new_part.append(129)
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


def make_subject_same_size(data, token=130):

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


def make_fugues_same_size(data, token=130):

    length = 0
    for d in data:
        if len(d) > length:
            length = len(d)


    length += 1
    new_data = []
    for d in data:
        while len(d) < length:
            d.append((token, token, token, token))
        new_data.append(d)

    return new_data


def make_dataset(pieces, active_voices):

    X = []
    Y = []

    new_pieces = []
    for n, piece in enumerate(pieces):
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
    Xoh = make_one_hot_vector(X, X.shape[0], X.shape[1])
    Yoh = make_one_hot_vector(Y, Y.shape[0], Y.shape[1])
    return X, Y, Xoh, Yoh


def do_transposition(fugue, interval):

    new_fugue = []

    for v in fugue:
        voice = []
        for n in v:
            if n >= 128:
                voice.append(n)
            else:
                voice.append(n+interval)
        new_fugue.append(voice)

    return new_fugue


def transpose_fugue(fugue, max_upward, max_downward):

    fugues = []
    upward = 0
    downward = 0

    if max_upward >= 6 and max_downward >= 6:
        upward = 6
        downward = 6
    elif max_upward < 6 and max_downward >= 6:
        upward = max_upward
        downward = 6
        while downward <= max_downward and downward <= 12-upward:
            downward += 1
    elif max_upward >= 6 and max_downward < 6:
        downward = max_downward
        upward = 6
        while upward <= max_upward and upward <= 12-downward:
            upward += 1
    elif max_upward < 6 and max_downward < 6:
        downward = max_downward
        upward = max_upward

    for interval in range(-downward, upward):
        fugues.append(do_transposition(fugue, interval))

    return fugues


def augment_data(fugues, active_voices):

    new_fugues = []
    new_active_voices = []

    for n, f in enumerate(fugues):
        max_upward = 0
        max_downward = 0

        max_note = 0
        min_note = 127
        for v in f:
            mx = max([None if (x > 127) else x for x in v])
            if mx > max_note:
                max_note = mx

            mn = min(v)
            if mn < min_note:
                min_note = mn

        max_upward = 127-max_note
        max_downward = min_note

        this_fugue = transpose_fugue(f, max_upward, max_downward)
        for a in range(len(this_fugue)):
            new_active_voices.append(active_voices[n])
        new_fugues.extend(this_fugue)

    return new_fugues, new_active_voices


if __name__ == '__main__':
    num_voices = 4
    step = 0.25
    files = get_file_names("fugueData/test")
    fugue_list = filter_file_list(files)
    fugues, active_voices = process_pieces(fugue_list)
    fugues, active_voices = augment_data(fugues, active_voices)
    dataset = make_dataset(fugues, active_voices)
    X, Y, Xoh, Yoh = return_data(dataset)
    final_dataset = {}
    final_dataset['X'] = X
    final_dataset['Y'] = Y
    final_dataset['Xoh'] = Xoh
    final_dataset['Yoh'] = Yoh
    pickle.dump(final_dataset, open("datasets/fugues.p", "wb"))

