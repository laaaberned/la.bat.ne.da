"""
Basic example: Generate a music video with simple beat sync.

Usage:
    python examples/basic_sync.py
"""

from beat_sync_func import BeatSyncPipeline, Config


def main():
    """Run basic music video generation."""
    
    # Load or create configuration
    config = Config.from_yaml('config/default.yaml')
    
    # Create pipeline
    pipeline = BeatSyncPipeline(config)
    
    # Process video
    output_video = pipeline.process(
        music_path='input/song.mp3',
        clip_pool_dir='input/clips/',
        output_path='output/music_video_v1.mp4',
        metadata={
            'artist': 'Example Artist',
            'title': 'Example Song',
            'tags': ['electronic', 'beat_sync'],
        },
    )
    
    print(f"\n✅ Video created: {output_video}")


if __name__ == '__main__':
    main()