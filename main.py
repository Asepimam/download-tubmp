import argparse
import sys
from youtube_convert import YouTubeConverter  # Pastikan nama kelas sudah benar

def main():
    parser = argparse.ArgumentParser(description="YouTube Downloader & Converter")
    parser.add_argument('-u', '--url', required=True, help="URL YouTube yang akan diunduh")
    parser.add_argument('-m', '--mp3', action='store_true', help="Konversi ke MP3")
    parser.add_argument('-vd', '--video', action='store_true', help="Unduh video")
    parser.add_argument('-o', '--output', default="downloads", help="Direktori output")
    parser.add_argument('-qty', '--quality', default="best", help="Kualitas video (misalnya: 1080, 720, 480)")

    args = parser.parse_args()

    # Inisialisasi converter
    converter = YouTubeConverter(output_dir=args.output)

    try:
        print(f"🔍 Memproses: {args.url}")

        if args.mp3:
            # Download dan konversi ke MP3
            mp3_path = converter.convert_audio(args.url)
            print(f"✅ Berhasil dikonversi ke MP3: {mp3_path}")

        elif args.video:
            # Download video dengan kualitas tertentu
            video_path = converter.download_video(args.url, quality=args.quality)
            print(f"✅ Video berhasil diunduh: {video_path}")

        else:
            print("⚠️ Pilih salah satu opsi: --mp3 atau --video")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
