import os
import sys
import logging
import argparse

# Add the root directory to sys.path to allow imports from src
sys.path.append(os.path.join(os.path.dirname(__file__)))

from src.playlist_generator import PlaylistGenerator

def main():
    parser = argparse.ArgumentParser(description="Generate Vavoo IPTV Playlist")
    parser.add_argument("--output", default="playlist.m3u8", help="Output path for the playlist")
    parser.add_argument("--groups", nargs="+", default=["Italy"], help="Groups to include")
    
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )

    logging.info(f"Starting playlist generation for groups: {args.groups}")
    gen = PlaylistGenerator()
    
    if gen.generate_m3u8(args.output, groups=args.groups):
        logging.info("Generation completed successfully.")
        sys.exit(0)
    else:
        logging.error("Failed to generate playlist.")
        sys.exit(1)

if __name__ == "__main__":
    main()
