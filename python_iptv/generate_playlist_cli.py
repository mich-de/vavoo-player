import os
import sys
import logging
import argparse

# Add the root directory to sys.path to allow imports from src
sys.path.append(os.path.join(os.path.dirname(__file__)))

from src.playlist_generator import PlaylistGenerator

def main():
    parser = argparse.ArgumentParser(description="Generate Vavoo IPTV Playlist")
    parser.add_argument("--output", default="playlist.m3u8", help="Output path for the standard playlist")
    parser.add_argument("--xc-output", help="Output path for the XCIPTV compatible playlist")
    parser.add_argument("--groups", nargs="+", default=["Italy", "Switzerland", "Vavoo"], help="Groups to include")
    
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
    
    success = True
    if args.output:
        logging.info(f"Generating Standard playlist...")
        if not gen.generate_m3u8(args.output, groups=args.groups, is_xc=False):
            success = False
            
    if args.xc_output:
        logging.info(f"Generating XCIPTV playlist...")
        if not gen.generate_m3u8(args.xc_output, groups=args.groups, is_xc=True):
            success = False
    
    if success:
        logging.info("Generation completed successfully.")
        sys.exit(0)
    else:
        logging.error("Failed to generate one or more playlists.")
        sys.exit(1)

if __name__ == "__main__":
    main()
