import json
import os
import sys

import yt_dlp

from errors import AgeRestrictionError, VideoUnavailableError, GeoRestrictedError, FormatNotAvailableError
from redis_client import r

proxy = '' if sys.platform == 'win32' else 'http://xray-host:12345'


def download_match_data(data: dict, key) -> dict | None:
    info = None
    last_reported = 0

    def progress_hook(d):
        nonlocal last_reported
        if d['status'] == 'downloading':
            current_percent = round(d.get('_percent', 0), 2)
            video_title = d.get('info_dict', {}).get('title', 'Unknown')
            if current_percent - last_reported >= 8 or current_percent == 100:
                r.lpush('answer', json.dumps({
                    "message_id": key,
                    "text": f"Скачивания видео.\nНазвание: {video_title}\nПрогресс: {current_percent}%\nСкорость: {d.get('_speed_str', 0)}\nОсталось: {d.get('_eta_str', 0)}",
                    "method": "text"
                }, ensure_ascii=False))
                last_reported = current_percent

    try:
        match data.get("service"):

            case "youtube":
                ydl_opts = {
                    'format': 'bv+ba',
                    'outtmpl': 'media/%(id)s%(format)s.%(ext)s',
                    'merge_output_format': 'm4a' if data.get("audio_only") else 'mp4',
                    'proxy': proxy,
                    'geo_bypass': True,
                    'max_filesize': 2147483648,
                    'retries': 10,
                    'no_warnings': True,
                    'progress_hooks': [progress_hook],
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    file = ydl.extract_info(data['id'], force_generic_extractor=False, download=False)

                formats_ids = ['401', '305', '400', '304', '399', '299', '266', '264', '137', '136', '135']
                # Скачиваем в зависимости от типа
                if data.get("audio_only"):
                    ydl_opts.update({
                        'merge_output_format': 'm4a',
                        'format': 'ba',
                    })
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        file = ydl.extract_info(data['id'], force_generic_extractor=False, download=True)
                else:
                    formats = []
                    ydl_opts['merge_output_format'] = 'mp4'
                    for f in file["formats"]:
                        filesize = f.get('filesize') or f.get('filesize_approx')
                        if not filesize:
                            filesize = 3147483648
                        if filesize < 2147483648 and f['ext'] == 'mp4' and 'avc1' in f.get('vcodec', '') and f['format_id'] in formats_ids:
                            formats.append(int(f['format_id']))

                    formats.sort(reverse=True)
                    for format_id in formats:
                        format_ = str(format_id) + '+ba'
                        ydl_opts['format'] = format_
                        try:
                            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                                file = ydl.extract_info(data['id'], force_generic_extractor=False, download=True)

                            break
                        except Exception as ex:
                            continue

                filename = ydl.prepare_filename(file)

                width, height = file['resolution'].split('x') if file['resolution'] != 'audio only' else [0, 0]
                info = {
                    "video_id": file['id'],
                    "height": int(height),
                    "width": int(width),
                    "duration": int(file['duration']),
                    "filename": os.path.basename(filename),
                    "title": file['title'],
                }
                r.hset(key, mapping=info)

            case "instagram":
                ydl_opts = {
                    'format': 'best',
                    'outtmpl': 'media/%(id)s.%(ext)s',
                    'proxy': proxy,
                    'quiet': True,
                    'progress_hooks': [progress_hook],
                }
                if data.get("audio_only"):
                    ydl_opts = {
                        'format': 'bestaudio/best',
                        'extract_audio': True,
                        'outtmpl': 'media/%(id)s.%(ext)s',
                        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                        }],
                    }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    file = ydl.extract_info(data["id"], download=True)

                    filename = ydl.prepare_filename(file)

                info = {
                    'height': int(file.get('height', 0)),
                    'width': int(file.get('width', 0)),
                    'duration': int(file.get('duration', 0)),
                    "filename": os.path.basename(filename),
                    "title": file['title'],
                }

                r.hset(key, mapping=info)

    except yt_dlp.utils.DownloadError as ex:
        error_msg = str(ex).lower()
        if 'unavailable' in error_msg:
            raise VideoUnavailableError from ex
        elif "unable to download video data" in error_msg:
            raise VideoUnavailableError from ex
        elif 'format' in error_msg:
            raise FormatNotAvailableError from ex
        elif 'geo restricted' in error_msg:
            raise GeoRestrictedError from ex
        elif 'sign in to confirm your age' in error_msg:
            raise AgeRestrictionError from ex
        raise ex

    return info
