from openai import OpenAI
import json


class HREvaluationAgent:
    def __init__(self, api_key: str):
        """
        Initialize the HR evaluation agent with the OpenAI API key.

        :param api_key: OpenAI API key for authentication
        """
        self.client = OpenAI(api_key=api_key)

    def _generate_prompt(self, question: str, answer: str) -> str:
        """
        Generate the prompt for evaluating an HR answer.

        :param question: The HR-related question
        :param answer: The answer provided by the candidate
        :return: The prompt string to be sent to the model
        """
        prompt = f"""
        You are an HR assistant helping to evaluate candidates' answers to interview questions. 
        Please evaluate the following answer based on **Relevance** criteria which is about does the answer directly address the question?

        Score relevancy on a scale of 1 to 10, where 10 is excellent and 1 is very poor. 

        Question: {question}
        Answer: {answer}

        Provide your evaluation in the following JSON format:
        {{
            "Relevance": [score out of 10],
        }}
        """
        return prompt

    def evaluate_answer(self, question: str, answer: str) -> dict:
        """
        Evaluate the provided answer based on multiple criteria and return the result as a JSON object.

        :param question: HR-related question
        :param answer: The answer provided by the candidate
        :return: A dictionary containing scores for each criterion and the overall evaluation.
        """
        prompt = self._generate_prompt(question, answer)

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "assistant", "content": prompt},
            ],
            response_format={"type": "json_object"},
        )
        evaluation_json = response.choices[0].message.content

        try:
            parsed_json = json.loads(evaluation_json)
        except json.JSONDecodeError:
            parsed_json = {"error": "Invalid JSON response from the API"}

        return parsed_json
