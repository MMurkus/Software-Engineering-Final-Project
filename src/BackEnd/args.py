import argparse


def get_args():
    parser = argparse.ArgumentParser(prog="Final-Project-SWEN")
    parser.add_argument(
        "--overwrite",
        help="Overwrite all data files",
        action="store_true",
    )
    parser.add_argument(
        "-v", "--verbose", help="Display print messages (TODO)", action="store_true"
    )
    return parser.parse_args()


def main():
    get_args()


if __name__ == "main":
    main()
