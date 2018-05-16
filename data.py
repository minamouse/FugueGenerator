from music21 import *


score = converter.parse("fugueData/goodFugues/fugue 4 [unknown].mid")

parts = [p for p in song.getElementsByClass(stream.Part)]

values = []
for p in parts:
    p.transferOffsetToElements()
    for m in p:
        time = m.offset - int(m.offset)
        if time != 0:
            values.append(time)

step = min(values)

