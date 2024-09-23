import argparse

from flask_ml.flask_ml_client import MLClient
from flask_ml.flask_ml_server.constants import DataTypes


# Define CLI arguments
def get_args():
    parser = argparse.ArgumentParser(description="Send audio to models for NER.")

    parser.add_argument(
        "--audio_files",
        nargs="+",
        required=True,
        help="List of audio file paths for transcription (e.g. data/audio.mp3 data/news.mp3).",
    )

    return parser.parse_args()


# Main function to handle audio transcription and NER
def main():
    AUDIO_TRANSCRIPTION_MODEL_URL = (
        "http://127.0.0.1:5000/transcriptionmodel"  # The URL of the server
    )
    NER_MODEL_URL = "http://127.0.0.1:5000/nermodel"

    # Audio TRANSCTIPTION
    client = MLClient(
        AUDIO_TRANSCRIPTION_MODEL_URL
    )  # Create an instance of the MLClient object

    # Get the audio file paths from CLI
    args = get_args()

    # Prepare the inputs dynamically from the CLI
    inputs = [{"file_path": audio_file} for audio_file in args.audio_files]

    data_type = DataTypes.AUDIO  # The type of the input data

    audio_transcription_response = client.request(
        inputs, data_type
    )  # Send a request to the server

    # NER MODEL
    client = MLClient(NER_MODEL_URL)  # Create an instance of the MLClient object

    inputs = [{"text": item["result"]} for item in audio_transcription_response]
    data_type = DataTypes.TEXT  # The type of the input data

    ner_response = client.request(inputs, data_type)  # Send a request to the server

    # Zip results from both responses to match filename to NER results
    no_of_files = len(audio_transcription_response)
    audio_ner_result = []
    for i in range(no_of_files):
        audio_ner_result = [
            {"file_path": f["file_path"], "result": r["result"]}
            for f, r in zip(audio_transcription_response, ner_response)
        ]

    print("RESULTS\n", audio_ner_result)


if __name__ == "__main__":
    main()
