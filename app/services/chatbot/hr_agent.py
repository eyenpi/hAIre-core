from openai import OpenAI
from typing import Dict
from app.services.chatbot.relevant_agent import HREvaluationAgent
from app.services.chatbot.clarification_agent import ClarificationAgent
from app.services.chatbot.cv_agent import HRCVQuestionAgent
import json


class HRQuestionnaireAgent:
    def __init__(self, api_key: str, config: dict):
        """
        Initialize the HR Questionnaire Agent as a microservice.

        :param api_key: OpenAI API key for authentication.
        :param questions: List of questions prepared by an HR expert.
        """
        self.client = OpenAI(api_key=api_key)

        self.questions = config["questions"]
        self.ask_from_cv = config["ask_from_cv"]
        if self.ask_from_cv:
            self.cv_agent = HRCVQuestionAgent(api_key)
            with open("assets/segmented_cv.json", "r") as f:
                cv_data = json.load(f)
            new_questions = self.cv_agent.generate_questions(cv_data, num_questions=3)
            for new_question in new_questions:
                self.questions.append(new_question)

        self.answers = []
        self.current_question_index = 0

        self.evaluation_agent = HREvaluationAgent(api_key)
        self.clarification_agent = ClarificationAgent(api_key)

    def handle_question_and_answer(self, answer: str = None) -> Dict[str, str]:
        """
        Handles both asking the next question and receiving the user's answer.

        :param answer: The answer provided by the candidate. If None, return the first or next question.
        :return: A dictionary with the next question or evaluation result.
        """
        # Check if all questions are completed
        if self.current_question_index >= len(self.questions):
            return {"status": "completed", "question": None}

        # If no answer provided (first call), return the first or next question
        if answer is None:
            question = self.questions[self.current_question_index]
            return {
                "status": "in_progress",
                "question": question,
            }

        # Process the provided answer
        question = self.questions[self.current_question_index]
        self.answers.append(answer)

        evaluation = self.evaluation_agent.evaluate_answer(question, answer)

        if evaluation.get("Relevance", 0) < 6:
            follow_up_question = self.clarification_agent.generate_clarification(
                question, answer
            )
            return {
                "status": "in_progress",
                "question": follow_up_question,
            }

        # Move to the next question if the answer is relevant
        self.current_question_index += 1

        # Check if there are more questions
        if self.current_question_index < len(self.questions):
            return {
                "status": "in_progress",
                "question": self.questions[self.current_question_index],
            }

        # If no more questions, mark the process as completed
        return {
            "status": "completed",
            "question": None,
        }
