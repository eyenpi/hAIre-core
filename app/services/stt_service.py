from app.models.stt_tts_model import STT


def get_text_of_sound(audio):
    model = STT()
    return model.execute(audio)