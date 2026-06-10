"""Main processing pipeline for ART.WE.ED.IT"""

from pathlib import Path
from typing import Dict, Any
from src.utils.config import Config
from src.utils.logger import get_logger, setup_logging
from src.beat_sync.audio_analyzer import AudioAnalyzer
from src.beat_sync.beat_detector import BeatDetector
from src.visual_analysis.clip_analyzer import ClipAnalyzer
from src.clip_selector.selector import ClipSelector
from src.timeline_generator.generator import TimelineGenerator, Timeline
from src.export.json_exporter import JSONExporter
from src.export.csv_exporter import CSVExporter

logger = get_logger(__name__)


class MusicVideoEditorPipeline:
    """Main pipeline orchestrating the complete workflow"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize pipeline with configuration"""
        self.config = Config(config_path)
        
        # Setup logging
        log_file = self.config.get("logging.log_file", "logs/art_we_ed_it.log")
        log_level = self.config.get("logging.level", "INFO")
        setup_logging(log_file, log_level)
        
        logger.info("Initializing ART.WE.ED.IT pipeline")
        
        # Initialize components
        audio_config = self.config.get_section("audio_analysis")
        self.audio_analyzer = AudioAnalyzer(
            sr=audio_config.get("sr", 22050),
            hop_length=audio_config.get("hop_length", 512),
            n_fft=audio_config.get("n_fft", 2048)
        )
        self.beat_detector = BeatDetector()
        
        visual_config = self.config.get_section("visual_analysis")
        self.clip_analyzer = ClipAnalyzer(
            sample_rate=visual_config.get("sample_rate", 2),
            target_fps=visual_config.get("target_fps", 30)
        )
        
        clip_selector_config = self.config.get_section("clip_selector")
        self.clip_selector = ClipSelector(
            max_consecutive_same_shot_scale=clip_selector_config.get("max_consecutive_same_shot_scale", 2),
            max_consecutive_same_mood=clip_selector_config.get("max_consecutive_same_mood", 3),
            weights=clip_selector_config.get("weights", {})
        )
        
        timeline_config = self.config.get_section("timeline_generator")
        self.timeline_generator = TimelineGenerator(
            transition_duration_ms=timeline_config.get("transition_duration_ms", 500),
            min_clip_duration_ms=timeline_config.get("min_clip_duration_ms", 500),
            max_clip_duration_ms=timeline_config.get("max_clip_duration_ms", 8000)
        )
        
        export_config = self.config.get_section("export")
        self.json_exporter = JSONExporter(indent=export_config.get("json_indent", 2))
        self.csv_exporter = CSVExporter(delimiter=export_config.get("csv_delimiter", ","))
        
        logger.info("Pipeline initialization complete")
    
    def process(
        self,
        audio_path: str,
        clips_dir: str,
        output_dir: str
    ) -> Dict[str, Any]:
        """
        Process music video end-to-end
        
        Args:
            audio_path: Path to audio file
            clips_dir: Directory containing video clips
            output_dir: Output directory for exports
            
        Returns:
            Dictionary with processing results
        """
        logger.info(f"Starting pipeline: {audio_path}")
        
        # Step 1: Analyze audio
        logger.info("Step 1: Analyzing audio...")
        audio_result = self.audio_analyzer.analyze(audio_path)
        
        # Step 2: Detect beats
        logger.info("Step 2: Detecting beats...")
        sync_points = self.beat_detector.find_sync_points(
            beats=audio_result.beats,
            bpm=audio_result.bpm,
            clip_count=10,  # Placeholder, will be determined by available clips
            allow_beat_division=self.config.get("timeline_generator.allow_beat_division", True)
        )
        
        # Step 3: Analyze video clips
        logger.info("Step 3: Analyzing video clips...")
        clips_dir = Path(clips_dir)
        clip_files = list(clips_dir.glob("*.mp4")) + list(clips_dir.glob("*.mov")) + list(clips_dir.glob("*.avi"))
        
        clip_metadata = []
        for clip_file in clip_files:
            try:
                metadata = self.clip_analyzer.analyze_clip(str(clip_file))
                clip_metadata.append(metadata)
            except Exception as e:
                logger.error(f"Error analyzing clip {clip_file}: {e}")
        
        if not clip_metadata:
            raise ValueError(f"No valid video clips found in {clips_dir}")
        
        logger.info(f"Analyzed {len(clip_metadata)} clips")
        
        # Step 4: Select clips
        logger.info("Step 4: Selecting clips...")
        selected_clips = self.clip_selector.select_clips(
            available_clips=clip_metadata,
            num_clips_needed=min(len(sync_points), len(clip_metadata)),
            sync_points=sync_points
        )
        
        # Step 5: Generate timeline
        logger.info("Step 5: Generating timeline...")
        timeline = self.timeline_generator.generate(
            selected_clips=selected_clips,
            beat_times=audio_result.beats,
            bpm=audio_result.bpm
        )
        
        # Step 6: Export results
        logger.info("Step 6: Exporting results...")
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        self.json_exporter.export_timeline(timeline, str(output_path / "timeline.json"))
        self.csv_exporter.export_timeline(timeline, str(output_path / "timeline.csv"))
        
        # Export clip analysis
        clip_analysis_data = [
            {
                "clip_id": clip.clip_id,
                "duration": clip.duration,
                "shot_scale": clip.shot_scale,
                "mood": clip.mood,
                "composition_score": clip.composition_score,
                "movement_intensity": clip.movement_intensity,
                "lighting_key": clip.lighting_key,
                "average_brightness": clip.average_brightness,
                "average_contrast": clip.average_contrast
            }
            for clip in clip_metadata
        ]
        self.csv_exporter.export_clip_analysis(clip_analysis_data, str(output_path / "clip_analysis.csv"))
        
        logger.info(f"Pipeline complete. Output saved to {output_dir}")
        
        return {
            "status": "success",
            "audio_analysis": {
                "bpm": audio_result.bpm,
                "duration": audio_result.metadata["duration_seconds"],
                "num_beats": audio_result.metadata["num_beats"]
            },
            "clips_analyzed": len(clip_metadata),
            "clips_selected": len(selected_clips),
            "timeline_duration_sec": timeline.total_duration_ms / 1000.0,
            "output_files": [
                str(output_path / "timeline.json"),
                str(output_path / "timeline.csv"),
                str(output_path / "clip_analysis.csv")
            ]
        }
