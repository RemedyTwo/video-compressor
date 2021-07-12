import tkinter as tk
from tkinter import filedialog
import json, os, subprocess, sys

ffmpeg_path = "ffmpeg"
ffprobe_path = "ffprobe"
config_file = json.load(open("config.json"))

def main(argv: str) -> None:
    file_path = "\"" + argv + "\""
    output_path = config_file.get("output path")
    output_resolution = config_file.get("output resolution")
    expected_size = config_file.get("expected size")
    audio_bitrate = config_file.get("audio bitrate")
    video_bitrate = get_bitrate_under_size_with_audio(file_path, audio_bitrate, expected_size)
    command1 = ffmpeg_path + " -y -i " + file_path + " -c:v libx264 -vf scale=\"" + str(output_resolution[0]) + ":" + str(output_resolution[1]) + "\" -b:v " + str(video_bitrate) + "k -pass 1 -an -f mp4 NUL"
    command2 = ffmpeg_path + " -y -i " + file_path + " -c:v libx264 -vf scale=\"" + str(output_resolution[0]) + ":" + str(output_resolution[1]) + "\" -b:v " + str(video_bitrate) + "k -pass 2 -c:a aac -b:a " + str(audio_bitrate) + "k " + output_path
    print(
        "command1: " + command1 + 
        "\ncommand2: " + command2
    )
    os.system(command1)
    os.system(command2)
    # Delete temp files from ffmpeg two-pass encoding
    os.remove("ffmpeg2pass-0.log")
    os.remove("ffmpeg2pass-0.log.mbtree")
    
    input("Process finished.")

def get_video_length(file_path: str) -> int:
    command = ffprobe_path + " -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 " + file_path
    output = str(subprocess.check_output(command, shell=True)).removeprefix("b'").removesuffix("\\r\\n'")
    output = int(float(output)) + 1
    return output

def get_bitrate_under_size(file_path: str, expected_size: int) -> int:
    # (200 MiB * 8192 [converts MiB to kBit]) / 600 seconds = ~2730 kBit/s total bitrate
    return int((expected_size * 8) / get_video_length(file_path))

def get_bitrate_under_size_with_audio(file_path: str, audio_bitrate: int, expected_size: int) -> int:
    return get_bitrate_under_size(file_path, expected_size) - audio_bitrate

if __name__ == "__main__":
    try:
        main(sys.argv[1])
    except IndexError:
        root = tk.Tk()
        root.withdraw()
        files = filedialog.askopenfilenames()
        for file in files:
            main(file)
