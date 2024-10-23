from app.services.chatbot.hr_agent import HRQuestionnaireAgent
from app.utils.file_reader import get_hr_questions
import os
from dotenv import load_dotenv

load_dotenv()


class AgentSingleton:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = HRQuestionnaireAgent(
                api_key=os.getenv("OPENAI_API_KEY"), questions=get_hr_questions()
            )
        return cls._instance

    @classmethod
    def update_instance(cls, questions):
        cls._instance = HRQuestionnaireAgent(
            api_key=os.getenv("OPENAI_API_KEY"), questions=questions
        )
        return cls._instance
