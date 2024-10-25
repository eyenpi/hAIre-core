from openai import OpenAI
from typing import List


class HRCVQuestionAgent:
    def __init__(self, api_key: str):
        """
        Initialize the HR question agent with the OpenAI API key for generating questions.

        :param api_key: OpenAI API key for authentication
        """
        self.client = OpenAI(api_key=api_key)

    def _generate_question_prompt(self, resume: dict) -> str:
        """
        Generate the prompt for asking general HR interview questions based on the resume content.

        :param resume: The candidate's resume as a string
        :return: The prompt string to be sent to the model
        """
        question_prompt = f"""
        You are an assistant conducting an HR interview. Based on the following resume:

        {resume}

        Ask one question from the interviewee to find out more about him based on his resume. Do not ask technical questions or any questions that reference company names, locations, personal names, or any specific detail in the description of the resume. The questions should focus on the candidate's work style, strengths, weaknesses, teamwork, and goals.
        Keep the question short and simple, and avoid including any personal information or details from the resume in the question.
        """
        return question_prompt

    def generate_questions(self, resume: str) -> List[str]:
        """
        Generate a set of general HR interview questions based on the provided resume.

        :param resume: The candidate's resume content
        :param num_questions: The number of questions to generate (default is 5)
        :return: A list of HR interview questions
        """
        question_prompt = self._generate_question_prompt(resume)

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "assistant", "content": question_prompt},
            ],
        )

        questions = [response.choices[0].message.content]
        return questions
