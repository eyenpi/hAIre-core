from openai import OpenAI
from typing import List


class HRTechnicalQuestionAgent:
    def __init__(self, api_key: str):
        """
        Initialize the HR question agent with the OpenAI API key for generating questions.

        :param api_key: OpenAI API key for authentication
        """
        self.client = OpenAI(api_key=api_key)

    def _generate_question_prompt(self, resume: dict, job_description) -> str:
        """
        Generate the prompt for asking general HR interview questions based on the resume content.

        :param resume: The candidate's resume as a string
        :return: The prompt string to be sent to the model
        """
        question_prompt = f"""
        You are an assistant conducting a technical interview. You are an expert in your field and you only ask short technical questions about the user and job description.
        Make sure to find patterns in the resume and job description and mention them in the question.
        Based on the following resume:

        {resume}

        and following job description:

        {job_description}

        Ask one technical question from the interviewee related to the skills, tools, technologies, and experiences mentioned in their resume that is related to the job description. Avoid any questions that reference specific company names, locations, personal names, or other identifiable details from the resume. 
        The question should be short and precise, focused on evaluating the candidate's technical knowledge, problem-solving skills, or expertise in relevant technologies, and should not be related to human resource at all. Make it pure technical.
        """
        return question_prompt

    def generate_questions(self, resume: str, job_description) -> List[str]:
        """
        Generate a set of general HR interview questions based on the provided resume.

        :param resume: The candidate's resume content
        :param num_questions: The number of questions to generate (default is 5)
        :return: A list of HR interview questions
        """
        question_prompt = self._generate_question_prompt(resume, job_description)

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "assistant", "content": question_prompt},
            ],
        )

        questions = [response.choices[0].message.content]
        return questions
