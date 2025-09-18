import subprocess
import sys



def merge(filename: str, filename_audio: str):
    command = ["ffmpeg", "-i", f"media/{filename}", "-i", f"media/{filename_audio}", "-map", "0:v", "-map",
                      "1:a", "-c:v", "copy", "-c:a", "copy", f"media/{filename}_out.mp4"]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    while True:
        output = process.stdout.readline()
        error = process.stderr.readline()

        if output == '' and error == '' and process.poll() is not None:
            break
        if output:
            print(output.strip())
        if error:
            print(error.strip(), file=sys.stderr)
    return process.poll()