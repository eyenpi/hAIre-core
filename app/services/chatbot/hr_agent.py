from openai import OpenAI
from typing import List, Dict
from app.services.chatbot.relevant_agent import HREvaluationAgent
from app.services.chatbot.clarification_agent import ClarificationAgent


class HRQuestionnaireAgent:
    def __init__(
        self,
        api_key: str,
        questions: List[str] = [
            "Where do you see yourself in the next 5 years?",
            "What is your biggest achievement?",
            "What is your biggest weakness?",
            "Why do you want to work with us?",
            "What are your salary expectations",
            "What are your hobbies?",
        ],
    ):
        """
        Initialize the HR Questionnaire Agent as a microservice.

        :param api_key: OpenAI API key for authentication.
        :param questions: List of questions prepared by an HR expert.
        """
        self.client = OpenAI(api_key=api_key)
        self.questions = questions
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
