import whisper


class STT:
    model = None

    def __init__(self):
        self.model = whisper.load_model("tiny")

    def execute(self, audio):
        return self.model.transcribe(audio)["text"]
