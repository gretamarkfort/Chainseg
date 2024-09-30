import argparse
from pathlib import Path

from planetai_chainseg.enricher.enricher_imu import EnricherIMU


def run():
    """
    Entry point to initiate the application based on the parsed command-line arguments.

    This function parses the command-line arguments and passes them to the main function.
    It's designed to kick off the application when the script is run as the main program.
    """
    main(parse_args())


def main(args):
    """
    Main execution function for processing the video stream.

    This function decides whether to operate in offline or online mode based on the presence of a file argument.
    In offline mode, it initializes a stream from a file, otherwise from a UDP stream.
    It also decides the type of visualizer to use based on the basic mode argument.

    Args:
    args (argparse.Namespace): Command-line arguments with the following attributes:
                                - args.file: Optional path to a video file for offline mode.
                                - args.basic: Boolean flag to use a basic visualizer without neural net processing.
    """

    from planetai_chainseg.stream.provider_file import StreamProviderFile
    from planetai_chainseg.stream.provider_udp import StreamProviderUDP
    from planetai_chainseg.visualizer.visualizer_basic import VisualizerBasic
    from planetai_chainseg.visualizer.visualizer_neural import VisualizerNeural

    offline_mode = args.file is not None
    basic_mode = args.basic

    if offline_mode:
        vid_path = Path(args.file)
        print(vid_path)
        p = StreamProviderFile(vid_path=vid_path, output_rgb=True, target_fps=30)
    else:
        p = StreamProviderUDP(output_rgb=True)

    if basic_mode:
        VisualizerBasic(provider=p, enrichers=[EnricherIMU()]).show()
    else:
        with VisualizerNeural(provider=p, enrichers=[EnricherIMU()]) as vis:
            vis.show()


def parse_args(args=None):
    """
    Parses command-line arguments.

    This function uses argparse to define and parse command-line arguments and returns them in a structured format.

    Args:
    args (list of str, optional): A list of strings representing the command-line arguments. If None, the default
                                  command-line arguments from sys.argv are used.

    Returns:
    argparse.Namespace: A namespace populated with the parsed command-line arguments.
    """

    parser = argparse.ArgumentParser(
        prog="OTC BlueROV Visual Assistant",
        description="Enriches an UDP video stream with neural net masks",
    )

    parser.add_argument(
        "--basic",
        "-b",
        default=False,
        action="store_true",
        help="skip neural net application",
    )

    parser.add_argument(
        "--file",
        "-f",
        default=None,
        type=str,
        help="if set apply on video file",
    )

    args = parser.parse_args(args=args)
    return args


if __name__ == "__main__":
    run()
