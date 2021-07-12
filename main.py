import json, os, tkinter, subprocess, sys
from tkinter import filedialog

ffmpeg_path = "ffmpeg"
ffprobe_path = "ffprobe"
config_file = json.load(open("config.json"))
output_path = config_file.get("output path")
output_resolution = config_file.get("output resolution")
expected_size = config_file.get("expected size") * 1000 # from kilobytes to bytes
audio_bitrate = config_file.get("audio bitrate") # kilobytes

def main(argv: str) -> None:
    file_path = "\"" + argv + "\""
    video_bitrate = get_bitrate_under_size_with_audio(file_path, audio_bitrate * 1000, expected_size)
    command1 = ffmpeg_path + " -y -i " + file_path + " -c:v libx264 -vf scale=\"" + str(output_resolution[0]) + ":" + str(output_resolution[1]) + "\" -b:v " + str(video_bitrate) + " -pass 1 -an -f mp4 NUL"
    command2 = ffmpeg_path + " -y -i " + file_path + " -c:v libx264 -vf scale=\"" + str(output_resolution[0]) + ":" + str(output_resolution[1]) + "\" -b:v " + str(video_bitrate) + " -pass 2 -c:a aac -b:a " + str(audio_bitrate) + "k " + output_path
    print(
        "pass 1: " + command1 + 
        "\npass 2: " + command2
    )
    subprocess.call(command1, creationflags=subprocess.CREATE_NEW_CONSOLE)
    print("First pass passed.")
    subprocess.call(command2, creationflags=subprocess.CREATE_NEW_CONSOLE)
    print("Second pass passed.")

    # Delete temp files from ffmpeg two-pass encoding
    os.remove("ffmpeg2pass-0.log")
    os.remove("ffmpeg2pass-0.log.mbtree")

    input("Compression complete. Press any key to exit...")

def get_video_length(file_path: str) -> int:
    '''Get length of the video path set in parameter.'''

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
    if (len(sys.argv) > 1):
        files = sys.argv[1:]
    else:
        root = tkinter.Tk()
        root.withdraw()
        files = filedialog.askopenfilenames(title = "Select video(s) to compress", filetypes = [("Video MP4", ".mp4")])

    for file in files:
        # Ignore file if already below wanted size
        if (os.path.getsize(file) > expected_size):
            main(file)
