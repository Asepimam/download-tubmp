import argparse
import sys
from youtube_convert import YouTubeToMP3Converter

def main():
    parser = argparse.ArgumentParser(description='Unduh YouTube ke MP3')
    parser.add_argument('url', help='URL YouTube')
    parser.add_argument('-o', '--output', default="downloads", help='Direktori output')

    args = parser.parse_args()

    converter = YouTubeToMP3Converter(output_dir=args.output)
    try:
        print(f"🔍 Memproses: {args.url}")
        print("⏬ Mengunduh audio...")
        mp3_path = converter.convert(args.url)
        print(f"✅ Berhasil disimpan di: {mp3_path}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
