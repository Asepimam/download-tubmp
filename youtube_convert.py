import os
import yt_dlp
from pydub import AudioSegment
import threading
import itertools
import time
from pydub.utils import which

class YouTubeToMP3Converter:
    def __init__(self, output_dir="downloads", tmp_dir="tmp"):
        self.output_dir = output_dir
        self.tmp_dir = tmp_dir
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.tmp_dir, exist_ok=True)

        # Path FFmpeg ke folder bin
        self.ffmpeg_path = os.path.join(os.path.dirname(__file__), 'ffmpeg', 'bin', 'ffmpeg.exe')
        self.ffprobe_path = os.path.join(os.path.dirname(__file__), 'ffmpeg', 'bin', 'ffprobe.exe')

        # Set ffmpeg dan ffprobe untuk pydub
        AudioSegment.converter = self.ffmpeg_path

        # Paksa pydub menggunakan ffprobe yang ditentukan
        os.environ["PATH"] += os.pathsep + os.path.dirname(self.ffmpeg_path)
        os.environ["FFPROBE"] = self.ffprobe_path

    def _download_audio(self, url: str) -> str:
        try:
            print("\U0001F4E5 Sedang mengunduh video...")
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(self.tmp_dir, '%(title)s.%(ext)s'),
                'ffmpeg_location': os.path.dirname(self.ffmpeg_path),
                'quiet': True,
                'no_warnings': True,
                'progress_hooks': [self._download_progress],
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                downloaded_file = ydl.prepare_filename(info)
                return downloaded_file
        except Exception as e:
            print(f"Gagal mengunduh audio: {e}")
            raise

    def _download_progress(self, d):
        if d['status'] == 'downloading':
            print(f"\U0001F4E5 Mengunduh... {d['_percent_str']} {d['_speed_str']}", end='\r')
        elif d['status'] == 'finished':
            print("\U0001F4E5 Unduhan selesai!                    ")

    def _convert_to_mp3(self, input_path: str) -> str:
        try:
            self._stop_loading = False
            loading_thread = threading.Thread(target=self._show_loading_animation)
            loading_thread.start()

            audio = AudioSegment.from_file(input_path)
            mp3_path = os.path.join(self.output_dir, os.path.splitext(os.path.basename(input_path))[0] + '.mp3')
            audio.export(mp3_path, format="mp3")

            os.remove(input_path)

            self._stop_loading = True
            loading_thread.join()

            return mp3_path
        except Exception as e:
            self._stop_loading = True
            print(f"Gagal mengonversi audio: {e}")
            raise

    def _show_loading_animation(self):
        for c in itertools.cycle(['|', '/', '-', '\\']):
            if self._stop_loading:
                break
            print(f'Proses konversi sedang berlangsung {c}', end='\r')
            time.sleep(0.1)
        print('Konversi selesai!                ')

    def convert(self, url: str) -> str:
        downloaded_file = self._download_audio(url)
        mp3_file = self._convert_to_mp3(downloaded_file)
        return mp3_file

    def convert_parallel(self, urls: list) -> list:
        threads = []
        results = []

        for url in urls:
            thread = threading.Thread(target=lambda u=url: results.append(self.convert(u)))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        return results
