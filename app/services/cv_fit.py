from openai import OpenAI
import json


class CVJobFitEvaluator:
    def __init__(self, api_key: str):
        """
        Initialize the CV job fit evaluator with the OpenAI API key.

        :param api_key: OpenAI API key for authentication
        """
        self.client = OpenAI(api_key=api_key)

    def _generate_prompt(self, user_cv: str, job_description: str) -> str:
        """
        Generate the prompt to evaluate the user's CV based on the job description.

        :param user_cv: The user's CV as a text string
        :param job_description: The job description as a text string
        :return: The prompt string to be sent to the model
        """
        prompt = f"""
        You are an HR assistant tasked with evaluating a candidate's CV to assess their fit for a specific job.
        Carefully review the candidate's CV in relation to the job description, identifying relevant skills, experiences, and qualifications.
        Based on the comparison, provide a score from 1 to 10 on how well the candidate's profile fits the job requirements, with 10 being an excellent fit and 1 being a poor fit.

        Return the response as a JSON object.

        Here is the job description:

        {job_description}

        And here is the candidate's CV:

        {user_cv}
        
        *Example output:*
        {{"score": <score from 1 to 10>}}


        Do not include any text outside of the JSON object in your response. Return an answer that I can easily decode using json.loads().
        """
        return prompt

    def evaluate_fit(self, user_cv: str, job_description: str) -> dict:
        """
        Evaluate the fit of the user's CV for the given job description and return a score from 1 to 10.

        :param user_cv: The user's CV content as a string
        :param job_description: The job description as a string
        :return: A dictionary containing the job fit score and detailed evaluation
        """
        prompt = self._generate_prompt(user_cv, job_description)

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "assistant", "content": prompt},
            ],
        )
        evaluation_content = response.choices[0].message.content
        score = evaluation_content

        # Parse JSON response directly
        score = (
            score.replace("json", "")
            .replace("```", "")
            .replace("\n", "")
            .replace(" ", "")
        )
        score = json.loads(score)
        score = int(score["score"])

        if score < 5:
            return {"result": False, "score": score}
        return {"result": True, "score": score}
