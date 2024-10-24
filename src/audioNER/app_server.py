import json
import textwrap
from typing import TypedDict
import warnings
from flask_ml.flask_ml_server import MLServer
from flask_ml.flask_ml_server.models import (
    FileInput,
    BatchFileInput,
    ResponseBody,
    BatchTextInput,
    BatchTextResponse,
    TextInput,
    TextResponse,
    MarkdownResponse,
    TaskSchema,
    InputSchema,
    InputType,
)

warnings.filterwarnings("ignore")


class AudioTranscription:
    def __init__(self) -> None:
        import whisper

        self.model = whisper.load_model("base")

    def predict(self, data: list[FileInput]) -> list:
        results = []
        for file in data:
            file_path = file.path
            results.append(self.model.transcribe(file_path)["text"])
        return results


class NER:
    def __init__(self) -> None:
        import spacy

        self.model = spacy.load("en_core_web_sm")

    def predict(self, data: list):
        results: list[list[dict[str, str]]] = []
        for i in range(len(data)):
            text = data[i].text
            ner_result = self.model(text)
            entities_list = [
                {"word/token": word.text, "entity_type": word.label_} for word in ner_result.ents
            ]
            results.append(entities_list)
        return results


# Create a server
server = MLServer(__name__)


def transcription_task_schema() -> TaskSchema:
    return TaskSchema(
        inputs=[
            InputSchema(
                key="audio_files",
                label="Audio Files",
                subtitle="Provide a collection of audio files to transcribe",
                input_type=InputType.BATCHFILE,
            )
        ],
        parameters=[],
    )


class AudioTranscriptionInputs(TypedDict):
    audio_files: BatchFileInput


class NoParameters(TypedDict):
    pass


# Create an endpoint
def run_transcription(inputs: AudioTranscriptionInputs, _parameters: NoParameters) -> ResponseBody:
    audio_transcription_model = AudioTranscription()
    input_files = inputs["audio_files"].files
    results = audio_transcription_model.predict(input_files)
    result_texts = [TextResponse(title=e.path, value=r) for e, r in zip(input_files, results)]
    return ResponseBody(root=BatchTextResponse(texts=result_texts))


@server.route(
    "/transcription", task_schema_func=transcription_task_schema, short_title="Audio Transcription", order=1
)
def run_transcription_flask_ml(inputs: AudioTranscriptionInputs, parameters: NoParameters) -> ResponseBody:
    return run_transcription(inputs, parameters)


def named_entity_recognition_task_schema() -> TaskSchema:
    return TaskSchema(
        inputs=[
            InputSchema(
                key="text_inputs",
                label="Text Inputs",
                subtitle="Provide a collection of text inputs to recognize named entities",
                input_type=InputType.BATCHTEXT,
            )
        ],
        parameters=[],
    )


class NerInputs(TypedDict):
    text_inputs: BatchTextInput


def run_named_entity_recognition(inputs: NerInputs, parameters: NoParameters) -> ResponseBody:
    ner_model = NER()
    text_inputs = inputs["text_inputs"].texts
    results = ner_model.predict(text_inputs)
    return ResponseBody(
        root=MarkdownResponse(
            title="NER Results",
            value="\n".join(
                [
                    textwrap.dedent(
                        f"""
## Input Text

{e.text}

## Entities Detected
{json.dumps(r, indent=4)}
                    """
                    )
                    for e, r in zip(text_inputs, results)
                ]
            ),
        )
    )


@server.route(
    "/named_entity_recognition",
    task_schema_func=named_entity_recognition_task_schema,
    short_title="Text Named Entity Recognition",
    order=2,
)
def run_named_entity_recognition_flask_ml(inputs: NerInputs, parameters: NoParameters) -> ResponseBody:
    return run_named_entity_recognition(inputs, parameters)


@server.route(
    "/transcription_and_named_entity_recognition",
    task_schema_func=transcription_task_schema,
    short_title="Audio Transcription and NER",
    order=0,
)
def process_audio_and_produce_ner(inputs: AudioTranscriptionInputs, parameters: NoParameters) -> ResponseBody:
    batch_text_response = run_transcription(inputs, parameters).root
    assert isinstance(batch_text_response, BatchTextResponse)
    texts = batch_text_response.texts
    ner_inputs: NerInputs = {"text_inputs": BatchTextInput(texts=[TextInput(text=t.value) for t in texts])}
    return run_named_entity_recognition(ner_inputs, parameters)


# Run the server (optional. You can also run the server using the command line)
if __name__ == "__main__":
    server.run()
