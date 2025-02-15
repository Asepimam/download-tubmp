from ffmpeg_downloader import installed

# Download dan install FFmpeg versi terbaru
ffmpeg_path = installed()
print(f"FFmpeg terpasang di: {ffmpeg_path}")
