from music21 import corpus, converter, note
from glob import glob
import pickle

num_voices = 4
step = 0.25


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


def filter_file_list(file_list):
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
        print(subject)
        X.append(subject)
        Y.append(zip(*piece))

    X = make_subject_same_size(X)
    Y = make_fugues_same_size(Y)
    return {'X': X, 'Y': Y}


def initialize_chorales():

    chorale_list = filter_file_list(corpus.getBachChorales(fileExtensions='xml'))
    chorales = process_pieces(chorale_list)
    dataset = make_dataset(chorales)
    pickle.dump(dataset, open("datasets/chorales.p", "wb"))


def initialize_fugues(files):

    fugue_list = filter_file_list(files)
    fugues, active_voices = process_pieces(fugue_list)
    dataset = make_dataset(fugues, active_voices)
    pickle.dump(dataset, open("datasets/fugues.p", "wb"))


