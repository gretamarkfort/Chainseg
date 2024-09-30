from pathlib import Path

from planetai_chainseg.enricher.enricher_imu import EnricherIMU
from planetai_chainseg.stream.provider_file import StreamProviderFile
from planetai_chainseg.visualizer.visualizer_neural import VisualizerNeural

if __name__ == "__main__":
    vid_path = Path.home() / "path" / "to" / "video_file"
    p = StreamProviderFile(vid_path=vid_path, output_rgb=True, target_fps=30)
    with VisualizerNeural(provider=p, enrichers=[EnricherIMU(offline_dummy=True)]) as vis:
        vis.show()
