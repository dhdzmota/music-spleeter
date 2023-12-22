from process_utils import (
    audio_from_yt,
    run_commands,
    merge_audios,
    pitch_change_file
)


if __name__ == '__main__':
    path = audio_from_yt()
    folder_path, file_path = run_commands(path)
    merge_audios(folder_path, file_path)
    pitch_change_file(folder_path, file_path)
