import os
import music21
from data import initialize_fugues


def get_file_names(path):

    names = []
    for f in os.listdir(path):
        new_path = os.path.join(path, f)
        if os.path.isfile(new_path):
            names.append(new_path)
        elif os.path.isdir(new_path):
            names.extend(get_file_names(new_path))

    return names


def validate(files):
    pieces = []
    for f in files:
        try:
            music21.converter.parse(f)
            pieces.append(f)
        except:
            print(f, "won't parse")
    return pieces

files = get_file_names("fugueData")
validated_files = validate(files)
initialize_fugues(validated_files)

