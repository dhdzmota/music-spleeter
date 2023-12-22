import os
import re
import subprocess
import librosa
import soundfile

from pydub import AudioSegment
from pytube import YouTube
from pytube.exceptions import RegexMatchError


def get_general_path():
    """
    Helper function to get the general path relative to this file.

    :return general_path: str
        String of the general path of the repo coming from the absolute path to
        this file.
    """
    file_path = os.path.dirname(os.path.abspath(__file__))
    general_path = os.path.join(file_path, '..')
    return general_path


def clean_string(string):
    """
    Helper function to clean string by lowering the capitals, replacing the
    spaces with underscores and keeping only alphanumerical values, and
    underscores as well.

    :param string: str
        String to clean.
    :return cleaned_str: str
        Cleaned string.

    """

    cleaned_str = string.lower()
    cleaned_str = cleaned_str.replace(' ', '_')
    cleaned_str = re.sub(r'\W+', '', cleaned_str)
    return cleaned_str


def audio_from_yt():
    """
    Function to obtain the audio from a YouTube link.

    :return file_path: str
        Path where the mp4 file is downloaded.
    """
    general_path = get_general_path()
    folder_name = 'audio_from_yt'
    folder_path = os.path.join(general_path, folder_name)
    output_dir = (os.listdir(folder_path))
    input_value = str(
        input('Enter the URL of the video you want to download: \n')
    )
    try:
        yt = YouTube(input_value)
        video = yt.streams.filter(only_audio=True).first()
        cleaned_video_title = clean_string(video.title)
        print(cleaned_video_title)
        video_title_file = f"{cleaned_video_title}.mp4"
        file_path = os.path.join(folder_path, video_title_file)

        if video_title_file in output_dir:
            print(f"File was already downloaded. Check your files:\n"
                  f"Name: {video_title_file}\n"
                  f"At: {folder_path}")
            return file_path

        video.download(output_path=folder_path, filename=video_title_file)
        print(f'File downloaded successfully:\n'
              f'Name: `{video_title_file}`\n'
              f'At: {folder_path}')
        return file_path

    except RegexMatchError:
        print(
            f'{input_value} is not a youtube link '
            f'or maybe there was an error.\n'
            ' Try again with a different url.')
        return None


def run_commands(file_path):
    """
    Function to run the 'spleeter' functionality to split a song in the
    corresponding components.

    :param file_path: str
        Path where the mp4 file resides (comes from the YouTube module).

    :return folder_path: str
        Path where the new songs will be stored.
    :return file_path: str
        Path where the main song is downloaded.
    """
    if file_path is None:
        return None

    general_path = get_general_path()
    folder_name = 'audio_output'
    folder_path = os.path.join(general_path, folder_name)

    split_num = input(
        "Input the number of instruments: \n\n"
        "- 2: for Vocals and Accompainment\n"
        "- 4: for Bass, Drums, Vocals, and Other\n"
        "- 5: for Bass, Drums, Piano, Vocals, and Other\n\n"
    )
    if split_num not in ['2', '4', '5']:
        split_num = '2'
        print('Getting the default number of instruments: 2')

    command_list = [
        f'spleeter separate '
        f'-c mp3 '
        f'-o {folder_path} '
        f'-p spleeter:{split_num}stems '
        f'{file_path}'
    ]
    for command in command_list:
        print(f'Getting music separation for number {split_num}...')
        subprocess.run(command.split(' '))
        print('Done with separation.')
    return folder_path, file_path


def get_audio_segment(file):
    """
    Helper function to get the audio segment.

    :param file: str
        String og the file to get an audio segment from.
    :return audio_segment AudioSegment:
        Audio segment file to process with pydub.
    """
    audio_segment = AudioSegment.from_file(file, format='mp3')
    return audio_segment


def get_path_of_files(folder_path, file_path):
    """
    Helper function to obtain the corresponding song folder in the output
    folders.

    :param folder_path: str
        Path where the new songs will be stored.
    :param file_path: str
        Path where the main song was downloaded.
    :return path_of_files: str
        Path of the corresponding song file's folder in output folder.
    """
    path_of_files = os.path.join(
        folder_path,
        file_path.split('/')[-1].replace('.mp4', '')
    )
    return path_of_files


def merge_audios(folder_path, file_path):
    """
    Function to merge the audios in an output folder_path by joining all but
    one. For example, if an output folder path contains the following output:
    ["piano.mp3", "voice.mp3", "drums.mp3"], this function would merge in
    the following way:
    - piano and voice, leaving out drums (without_drums.mp3)
    - piano and drums, leaving out voice (without_voice.mp3)
    - drums and voice, leaving out drums (without_piano.mp3)


    :param folder_path: str
        Path where the new songs will be stored.
    :param file_path: str
        Path where the main song was downloaded.
    :return:
        None
    """
    print('Starting to merge audios...')

    path_of_files = get_path_of_files(folder_path, file_path)

    files_to_process = os.listdir(path_of_files)

    if len(files_to_process) <= 2:
        print('There is nothing to do.')
        return None
    for file in files_to_process:
        filename = file.split('.')[0]
        temporary_files_to_process = files_to_process[:]
        temporary_files_to_process.remove(file)

        segments = [get_audio_segment(f'{path_of_files}/{tmp_f}')
                    for tmp_f in temporary_files_to_process]
        song = segments[0]
        for s in segments[1:]:
            song = song.overlay(s, position=0)
        final_file_path_name = f"{path_of_files}/without_{filename}.mp3"
        song.export(final_file_path_name, format="mp3")
        print(
            f'Merging audio parts, getting the file: \n'
            f'{final_file_path_name}'
        )
        print('Done. With process')


def pitch_change(filename):
    """
    Helper function to apply the pitch change and save the corresponding songs.
    The pitches go automatically from -5 semitones to 5 semitones in steps of
    two (remember that 12 tones represent a complete octave).

    :param filename:
    :return:
    """
    path_splitted = filename[::-1].split('/', 1)
    path_to_file = path_splitted[-1][::-1]
    filename_to_change = path_splitted[0][::-1]
    y, sr = librosa.load(filename)
    for steps in range(-5, 5, 2):
        new_filename = filename_to_change.replace('.', f'__{steps}.')
        new_y = librosa.effects.pitch_shift(y, sr=sr, n_steps=steps)
        new_path = os.path.join(path_to_file, new_filename)
        soundfile.write(new_path, new_y, sr)
        print(f'writing song with new pitch in: \n {new_path}')


def pitch_change_file(folder_path, file_path):
    """
    Logic to apply a pitch change to the without_vocals file or the
    accompaniment file. To practice other tones to sing in.

    :param folder_path: str
        Path where the new songs will be stored.
    :param file_path: str
        Path where the main song was downloaded.
    :return:
        None
    """
    value = str(input('Do you want to have different pitches?: y/n \n'))
    if value == 'y':
        path_of_files = get_path_of_files(folder_path, file_path)
        files_to_process = os.listdir(path_of_files)
        desired_f = 'without_vocals.mp3', 'accompaniment.mp3'
        if desired_f[0] in files_to_process:
            new_path = os.path.join(path_of_files, desired_f[0])
        elif desired_f[1] in files_to_process:
            new_path = os.path.join(path_of_files, desired_f[0])
        pitch_change(new_path)
    else:
        print('We assume that was a no. There is nothing to do')
    print('Done with everything.')
