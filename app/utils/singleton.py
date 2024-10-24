from app.services.chatbot.hr_agent import HRQuestionnaireAgent
from app.utils.file_reader import get_hr_config
import os
from dotenv import load_dotenv

load_dotenv()


class AgentSingleton:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = HRQuestionnaireAgent(
                api_key=os.getenv("OPENAI_API_KEY"), config=get_hr_config()
            )
        return cls._instance

    @classmethod
    def update_instance(cls, config):
        cls._instance = HRQuestionnaireAgent(
            api_key=os.getenv("OPENAI_API_KEY"), config=config
        )
        return cls._instance
