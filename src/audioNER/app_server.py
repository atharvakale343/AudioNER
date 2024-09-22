import spacy
import whisper
from flask_ml.flask_ml_server import MLServer
from flask_ml.flask_ml_server.constants import DataTypes
from flask_ml.flask_ml_server.models import (AudioResult, ResponseModel,
                                             TextResult)


class AudioTranscription:
    def __init__(self) -> None:
        self.model = whisper.load_model("base")

    def predict(self, data: list) -> list:
        results = []
        for file in data:
            file_path = file.file_path
            results.append(self.model.transcribe(file_path)["text"])
        return results


class NER:
    def __init__(self) -> None:
        self.model = spacy.load("en_core_web_sm")

    def predict(self, data: list) -> list:
        results = []
        for i in range(len(data)):
            text = data[i].text
            ner_result = self.model(text)
            entities_list = [
                {"word/token": word.text, "entity_type": word.label_}
                for word in ner_result.ents
            ]
            results.append(entities_list)
        return results


# create an instance of the model
AudioTranscriptionModel = AudioTranscription()
NERModel = NER()

# Create a server
server = MLServer(__name__)


# Create an endpoint
@server.route("/transcriptionmodel", DataTypes.AUDIO)
def process_audio(inputs: list, parameters: dict) -> dict:
    results = AudioTranscriptionModel.predict(inputs)
    results = [
        AudioResult(file_path=e.file_path, result=r) for e, r in zip(inputs, results)
    ]
    response = ResponseModel(results=results)
    return response.get_response()


@server.route("/nermodel", DataTypes.TEXT)
def process_text(inputs: list, parameters: dict) -> dict:
    results = NERModel.predict(inputs)
    results = [TextResult(text=e.text, result=r) for e, r in zip(inputs, results)]
    response = ResponseModel(results=results)
    return response.get_response()


# Run the server (optional. You can also run the server using the command line)
server.run()
