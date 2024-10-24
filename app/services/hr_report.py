from openai import OpenAI
from app.utils.pdf import generate_pdf_report


class HRReportGenerator:
    def __init__(self, api_key: str):
        """
        Initialize the HR report generator assistant with the OpenAI API key.

        :param api_key: OpenAI API key for authentication
        """
        self.client = OpenAI(api_key=api_key)

    def _generate_prompt(self, conversation: str, criteria: list[str]) -> str:
        """
        Generate the prompt for creating a human-readable evaluation report based on the interview conversation.

        :param conversation: The transcript of the interview conversation
        :param criteria: A list of evaluation criteria to be included in the report
        :return: The prompt string to be sent to the model
        """
        # Create a formatted string for the criteria
        criteria_text = "\n".join([f"<b>{criterion}</b>" for criterion in criteria])

        prompt = f"""
        You are an HR assistant tasked with evaluating a candidate's interview responses and providing a detailed, human-readable report for the HR manager.
        The report should focus on the following criteria for each answer:
        
        {criteria_text}

        For each question, provide feedback on how well the candidate answered, highlight any strengths or concerns, and offer a brief summary of the candidate's overall performance.

        End the report with a final recommendation to the HR manager, including whether the candidate should move forward in the hiring process, and any suggested follow-up questions or clarifications.
        Use HTML tags for formatting to enhance readability anywhere necessary.

        Here is the transcript of the conversation:

        {conversation}

        Please structure the report as follows:

        <b>Question 1</b>: [First question]
        <b>Candidate's Response</b>: [First response]
        <b>Evaluation</b>: [Detailed evaluation of the candidate’s answer. Mention the provided criteria for evaluation and give an overall assessment.]

        <b>Question 2</b>: [Second question]
        <b>Candidate's Response</b>: [Second response]
        <b>Evaluation</b>: [Detailed evaluation of the candidate’s answer...]

        <h2><b>Overall Assessment</b></h2>
        [Provide an overall assessment summarizing the candidate's performance across all questions, identifying strengths, areas of improvement, and consistency across answers.]

        </h2><b>Final Recommendation</b></h2>
        [Give a recommendation on whether the candidate should be considered for the next stage of the process and what could be improved.]
        ---
        """
        return prompt

    def generate_report(
        self, conversation: str, file_path: str, criteria: list[str]
    ) -> str:
        """
        Generate a detailed, human-readable evaluation report for the interview based on the provided conversation.

        :param conversation: The interview conversation (questions and answers)
        :return: A formatted human-readable report as a string.
        """
        prompt = self._generate_prompt(conversation, criteria=criteria)

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "assistant", "content": prompt},
            ],
        )
        report_content = response.choices[0].message.content

        generate_pdf_report(file_path, report_content)

        return report_content
