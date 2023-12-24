from chord_extractor.extractors import Chordino

# TODO: See what can we do with this.

chordino = Chordino(roll_on=0)
conversion_file_path = './audio_output/satellite/without_vocals.mp3'

chords = chordino.extract(conversion_file_path)
print(chords)

conversion_file_path = './audio_output/satellite/without_vocals__1.mp3'
chords = chordino.extract(conversion_file_path)
print(chords)