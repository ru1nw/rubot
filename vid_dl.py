import os
import subprocess
import sys
import re

async def dl(link, *, audio=False, worst=False):
    # get title and duration
    try:
        check = subprocess.run(["youtube-dl", "-e", "--get-duration", link],
                               capture_output=True, timeout=10)
    except subprocess.TimeoutExpired as err:
        raise DlError(err, "[ERR] timed out, \
possibly caused by url linking to a playlist or channel")

    # check if error is output
    try:
        check.check_returncode()
    except subprocess.CalledProcessError as err:
        if b"HTTP Error" in err.stderr:
            raise DlError(err, "[ERR] HTTP error\n")
        elif b"Video unavailable" in err.stderr:
            raise DlError(err, "[ERR] video unavailable, \
possibly caused by an invalid id or deleted/blocked video\n")
        elif b"Unsupported URL" in err.stderr:
            raise DlError(err, "[ERR] unsupported url, \
possibly caused by unsupported website or incomplete url\n")
        elif ((b"is not a valid URL" in err.stderr)
              or (b"getaddrinfo failed" in err.stderr)):
            raise DlError(err, "[ERR] not a url\n")
        else:
            raise DlError(err, "[ERR] unknown error\n")

    # process stdout
    out = check.stdout.strip().split(b"\n")
    if len(out) > 2:
        raise DlError(RuntimeError, "[ERR] more than one video was returned\n")
    elif len(out) < 2:
        raise DlError(RuntimeError, "[ERR] youtube-dl didn't return anything\n")
    byte_name, byte_time = out

    # check video duration
    time = byte_time.decode().strip().split(":")
    if (((len(time) > 2) and (eval(time[-3]) > 0))
            or (len(time) > 1 and (eval(time[-2]) > 10))):
        raise DlError(RuntimeError, "[ERR] video over 10 mins long\n")

    # decode video title
    try:
        filename = byte_name.decode(sys.getfilesystemencoding())
    except UnicodeDecodeError:
        try:
            filename = byte_name.decode('big5')
        except UnicodeDecodeError:
            filename = subprocess.run(
                ["youtube-dl", "--get-id", link],
                capture_output=True).stdout.decode(sys.getfilesystemencoding())
    if worst:
        filename += "2"
    filename += ".mp3" if audio else ".mp4"
    filename = re.sub('\/|\\\\|:|\*|\?|"|<|>|\|', "", filename)

    args = ["youtube-dl", "-o", filename, link]
    if worst and audio:
        args += ["-f", "worstaudio"]
    elif worst:
        args += ["-f", "worst"]
    if audio:
        args += ["-x", "--audio-format", "mp3"]
    else:
        args += ["--merge-output-format", "mp4"]
    y = subprocess.run(args, capture_output=True)
    y.check_returncode()

    return (os.getcwd() + r"/" + filename)

class DlError(Exception):
    """Exception raised for errors in dl().

    Attributes:
        error -- the error originally raised
    """

    def __init__(self, error, simple_errmsg):
        self.error = error
        self.name = type(error).__name__
        self.simple_errmsg = simple_errmsg

    def __str__(self):
        return self.simple_errmsg
