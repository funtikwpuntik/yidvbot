import subprocess

def make_url(_id: str):
    return f"https://www.youtube.com/watch?v={_id}"

def translate(_id: str):
    url = make_url(_id)
    command = ["vot-cli", "--output=/app/media", f"--output-file={_id}.mp3", url]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    while True:
        output = process.stdout.readline()
        error = process.stderr.readline()

        if output == '' and error == '' and process.poll() is not None:
            break
        if output:
            print(output.strip())
        if error:
            raise Exception(error.strip())
    return process.poll()
