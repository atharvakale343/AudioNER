# cli.py

import argparse

from flask_ml.flask_ml_cli import MLCli
from .app_server import server


def main():
    parser = argparse.ArgumentParser(description="Audio Transcription and Named Entity Recognition (NER)")
    cli = MLCli(server, parser)
    cli.run_cli()


if __name__ == "__main__":
    main()
