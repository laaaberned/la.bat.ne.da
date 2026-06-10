"""
CLI commands for rendering.
"""

import click
from pathlib import Path
from loguru import logger

from beat_sync_func.core.rendering_pipeline import RenderingBeatSyncPipeline
from beat_sync_func.core.config import Config
from beat_sync_func.utils.logging import setup_logging


@click.command()
@click.option('--music', '-m', required=True, help='Path to music file (MP3, WAV, etc.)')
@click.option('--clips', '-c', required=True, help='Path to clips directory')
@click.option('--output', '-o', required=True, help='Output video path')
@click.option('--config', default='config/default.yaml', help='Configuration file')
@click.option('--fps', type=int, default=None, help='Output FPS (overrides config)')
@click.option('--quality', type=int, default=None, help='Video quality/CRF (0-51, lower=better)')
@click.option('--resolution', default=None, help='Output resolution (e.g., 1920x1080)')
@click.option('--no-gpu', is_flag=True, help='Disable GPU acceleration')
@click.option('--debug', is_flag=True, help='Enable debug mode')
def render(
    music: str,
    clips: str,
    output: str,
    config: str,
    fps: int,
    quality: int,
    resolution: str,
    no_gpu: bool,
    debug: bool,
):
    """Render a beat-synced music video.
    
    Example:
        beat-sync render --music song.mp3 --clips ./clips --output video.mp4
    """
    
    # Setup logging
    setup_logging(debug_mode=debug)
    
    try:
        logger.info("🎬 BEAT SYNC RENDERER v0.1.0")
        logger.info("Initializing...\n")
        
        # Load configuration
        cfg = Config.from_yaml(config)
        cfg.debug_mode = debug
        cfg.use_gpu = not no_gpu
        
        # Override config with CLI parameters
        if fps:
            cfg.video.fps = fps
        if quality is not None:
            cfg.video.quality = quality
        if resolution:
            try:
                w, h = map(int, resolution.split('x'))
                cfg.video.resolution = (w, h)
            except:
                logger.error("Invalid resolution format. Use: 1920x1080")
                raise
        
        # Create pipeline
        pipeline = RenderingBeatSyncPipeline(cfg, detect_hardware=True)
        
        # Process video
        output_video = pipeline.process(
            music_path=music,
            clip_pool_dir=clips,
            output_path=output,
        )
        
        click.secho(f"\n\u2705 Done! Video saved to: {output_video}", fg='green', bold=True)
        
    except FileNotFoundError as e:
        logger.error(f"\u274c File not found: {e}")
        raise click.Exit(1)
    except ValueError as e:
        logger.error(f"\u274c Invalid input: {e}")
        raise click.Exit(1)
    except Exception as e:
        logger.error(f"\u274c Error: {e}")
        if debug:
            logger.exception("Full traceback:")
        raise click.Exit(1)


if __name__ == '__main__':
    render()
