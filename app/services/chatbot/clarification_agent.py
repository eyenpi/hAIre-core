from openai import OpenAI


class ClarificationAgent:
    def __init__(self, api_key: str, threshold: int = 6):
        """
        Initialize the clarification agent with the OpenAI API key and a threshold for detecting unclear answers.

        :param api_key: OpenAI API key for authentication
        """
        self.client = OpenAI(api_key=api_key)

    def _generate_clarification_prompt(self, question: str, answer: str) -> str:
        """
        Generate the prompt for rephrasing or asking a clarifying question.

        :param question: The original question asked
        :param evaluation: The evaluation of the candidate's answer
        :return: The prompt string to be sent to the model
        """
        clarification_prompt = f"""
        You are an assistant conducting HR interviews. The candidate's response to the following question was unclear or irrelevant:
        {question}

        The answer of user was:
        {answer}

        Provide a rephrased or clarifying question to help the candidate better understand the original question. Keep the question clear and concise.
        """
        return clarification_prompt

    def generate_clarification(self, question: str, evaluation: dict) -> str:
        """
        Generate a clarification or rephrased question based on the evaluation scores.

        :param question: The original question
        :param evaluation: The evaluation dictionary containing scores for relevance, clarity, etc.
        :return: A clarification or rephrased question if necessary
        """
        clarification_prompt = self._generate_clarification_prompt(question, evaluation)

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "assistant", "content": clarification_prompt},
            ],
            max_tokens=1000,
        )

        return response.choices[0].message.content
