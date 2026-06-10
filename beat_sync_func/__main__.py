"""
CLI entry point for BEAT SYNC FUNC.
"""

import sys
from pathlib import Path
import click
from loguru import logger

from beat_sync_func import BeatSyncPipeline, Config
from beat_sync_func.utils.logging import setup_logging


@click.command()
@click.option('--music', '-m', required=True, help='Path to music file')
@click.option('--clips', '-c', required=True, help='Path to clips directory')
@click.option('--output', '-o', required=True, help='Output video path')
@click.option('--config', default='config/default.yaml', help='Configuration file')
@click.option('--debug', is_flag=True, help='Enable debug mode')
def main(
    music: str,
    clips: str,
    output: str,
    config: str,
    debug: bool,
):
    """Generate a beat-synced music video."""
    
    # Setup logging
    setup_logging(debug_mode=debug)
    
    try:
        # Load configuration
        logger.info(f"🎬 BEAT SYNC FUNC v0.1.0")
        cfg = Config.from_yaml(config)
        cfg.debug_mode = debug
        
        # Create pipeline
        pipeline = BeatSyncPipeline(cfg)
        
        # Process video
        output_video = pipeline.process(
            music_path=music,
            clip_pool_dir=clips,
            output_path=output,
        )
        
        logger.success(f"\n✅ Done! Video saved to: {output_video}")
        
    except FileNotFoundError as e:
        logger.error(f"❌ File not found: {e}")
        sys.exit(1)
    except ValueError as e:
        logger.error(f"❌ Invalid input: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        if debug:
            logger.exception("Full traceback:")
        sys.exit(1)


if __name__ == '__main__':
    main()