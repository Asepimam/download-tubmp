import os
import yt_dlp
from pydub import AudioSegment
import threading
import itertools
import time
import tempfile
from pathlib import Path

class YouTubeConverter:
    def __init__(self, output_dir=None, tmp_dir=None):
        # Tentukan direktori default
        home_dir = Path.home()
        # Menentukan direktori default untuk download
        if output_dir is None:
            output_dir = home_dir / "Downloads"

        # Menentukan direktori default untuk tmp
        if tmp_dir is None:
            tmp_dir = Path(tempfile.gettempdir())  # Misalnya: /tmp di Linux/macOS

        self.output_dir = Path(output_dir)
        self.tmp_dir = Path(tmp_dir)

        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.tmp_dir, exist_ok=True)

        # Path ke FFmpeg
        self.ffmpeg_path = os.path.join(os.path.dirname(__file__), 'ffmpeg', 'bin', 'ffmpeg.exe')
        self.ffprobe_path = os.path.join(os.path.dirname(__file__), 'ffmpeg', 'bin', 'ffprobe.exe')

        # Konfigurasi FFmpeg untuk Pydub
        AudioSegment.converter = self.ffmpeg_path
        os.environ["PATH"] += os.pathsep + os.path.dirname(self.ffmpeg_path)
        os.environ["FFPROBE"] = self.ffprobe_path

    def remove_query_url(self, url: str) -> str:
        """Menghapus query tambahan dari URL YouTube."""
        return url.split('&')[0]

    def _download_audio(self, url: str) -> str:
        """Mengunduh hanya audio dari video YouTube."""
        url = self.remove_query_url(url)
        try:
            print("\U0001F4E5 Mengunduh audio...")
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': str(self.tmp_dir / '%(title)s.%(ext)s'),
                'ffmpeg_location': os.path.dirname(self.ffmpeg_path),
                'quiet': True,
                'no_warnings': True,
                'progress_hooks': [self._download_progress],
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                return ydl.prepare_filename(info)
        except Exception as e:
            print(f"\U0000274C Gagal mengunduh audio: {e}")
            raise

    def _download_video(self, url: str, quality: str = "best") -> str:
        """Mengunduh video dengan kualitas yang bisa dipilih."""
        url = self.remove_query_url(url)
        try:
            print("\U0001F4E5 Mengunduh video...")
            format_str = f'bestvideo[height<={quality}]+bestaudio/best' if quality.isdigit() else 'best'
            ydl_opts = {
                'format': format_str,
                'outtmpl': str(self.output_dir / '%(title)s.%(ext)s'),
                'ffmpeg_location': os.path.dirname(self.ffmpeg_path),
                'quiet': True,
                'no_warnings': True,
                'progress_hooks': [self._download_progress],
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                return ydl.prepare_filename(info)
        except Exception as e:
            print(f"\U0000274C Gagal mengunduh video: {e}")
            raise

    def _download_progress(self, d):
        """Menampilkan progress saat download."""
        if d['status'] == 'downloading':
            print(f"\U0001F4E5 Mengunduh... {d['_percent_str']} {d['_speed_str']}", end='\r')
        elif d['status'] == 'finished':
            print("\U0001F4E5 Unduhan selesai!                    ")

    def _convert_to_mp3(self, input_path: str) -> str:
        """Mengonversi file audio ke MP3."""
        try:
            self._stop_loading = False
            threading.Thread(target=self._show_loading_animation, daemon=True).start()

            audio = AudioSegment.from_file(input_path)
            mp3_path = self.output_dir / (Path(input_path).stem + '.mp3')
            audio.export(mp3_path, format="mp3")

            os.remove(input_path)

            self._stop_loading = True
            return str(mp3_path)
        except Exception as e:
            self._stop_loading = True
            print(f"\U0000274C Gagal mengonversi audio: {e}")
            raise

    def _show_loading_animation(self):
        """Menampilkan animasi loading selama proses konversi."""
        for c in itertools.cycle(['|', '/', '-', '\\']):
            if self._stop_loading:
                break
            print(f'Proses konversi sedang berlangsung {c}', end='\r')
            time.sleep(0.1)
        print('Konversi selesai!                ')

    def convert_audio(self, url: str) -> str:
        """Mengunduh dan mengonversi video YouTube ke MP3."""
        downloaded_file = self._download_audio(url)
        return self._convert_to_mp3(downloaded_file)

    def download_video(self, url: str, quality: str = "best") -> str:
        """Mengunduh video dengan kualitas tertentu."""
        return self._download_video(url, quality)

    def convert_parallel(self, urls: list, is_audio=True, quality="best") -> list:
        """Mengonversi beberapa URL secara paralel."""
        threads = []
        results = []

        for url in urls:
            if is_audio:
                thread = threading.Thread(target=lambda u=url: results.append(self.convert_audio(u)))
            else:
                thread = threading.Thread(target=lambda u=url: results.append(self.download_video(u, quality)))
            
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        return results
