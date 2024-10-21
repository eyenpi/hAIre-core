from openai import OpenAI
from typing import List, Dict
from app.services.chatbot.relevant_agent import HREvaluationAgent
from app.services.chatbot.clarification_agent import ClarificationAgent


class HRQuestionnaireAgent:
    def __init__(self, api_key: str, questions: List[str]):
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

    def ask_question(self) -> Dict[str, str]:
        """
        Return the current question to be asked.

        :return: A dictionary with the current question and the current question index.
        """
        if self.current_question_index >= len(self.questions):
            return {"status": "completed", "message": "All questions have been asked."}

        question = self.questions[self.current_question_index]
        return {
            "status": "in_progress",
            "question": question,
            "current_question_index": self.current_question_index,
            "total_questions": len(self.questions),
        }

    def receive_answer(self, answer: str) -> Dict[str, str]:
        """
        Process the user's answer, evaluate it, and either ask the next question or generate a follow-up clarification question.

        :param answer: The answer provided by the candidate.
        :return: A dictionary with the evaluation result or follow-up question if clarification is needed.
        """
        question = self.questions[self.current_question_index]
        self.answers.append(answer)

        evaluation = self.evaluation_agent.evaluate_answer(question, answer)
        print(f"Evaluation: {evaluation}")

        if evaluation.get("Relevance", 0) < 6:
            follow_up_question = self.clarification_agent.generate_clarification(
                question, answer
            )
            return {
                "status": "clarification_needed",
                "follow_up_question": follow_up_question,
                "current_question_index": self.current_question_index,
            }

        self.current_question_index += 1
        if self.current_question_index < len(self.questions):
            return {
                "status": "in_progress",
                "next_question": self.questions[self.current_question_index],
                "current_question_index": self.current_question_index,
                "total_questions": len(self.questions),
            }
        else:
            return {
                "status": "completed",
                "answers": self.answers,
                "message": "All questions have been asked and answered.",
            }
