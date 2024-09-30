from planetai_chainseg.enricher.enricher_imu import EnricherIMU
from planetai_chainseg.stream.provider_udp import StreamProviderUDP
from planetai_chainseg.visualizer.visualizer_neural import VisualizerNeural

if __name__ == "__main__":
    p = StreamProviderUDP(output_rgb=True)
    # We expect that you run with a ROV attached, so the EnricherIMU is initialized without offline_dummy=True
    with VisualizerNeural(provider=p, enrichers=[EnricherIMU()]) as vis:
        vis.show()
