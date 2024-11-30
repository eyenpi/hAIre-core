from openai import OpenAI
from app.utils.pdf import generate_pdf_report, generate_short_report
from app.utils.file_reader import get_hr_config
import json


class HRReportGenerator:
    def __init__(self, api_key: str):
        """
        Initialize the HR report generator assistant with the OpenAI API key.

        :param api_key: OpenAI API key for authentication
        """
        self.client = OpenAI(api_key=api_key)
        self.config = get_hr_config()
        self.job_description = self.config["job_info"]

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

        For each question, provide feedback on how well the candidate answered, highlight any strengths or concerns, and offer a brief summary of the candidate's overall performance according to the job description.
        Make sure to mention the relevant part of the job description in your evaluation.

        End the report with a final recommendation to the HR manager, including whether the candidate should move forward in the hiring process, and any suggested follow-up questions or clarifications according to the job description given below.
        Use HTML tags for formatting to enhance readability anywhere necessary.

        Here is the transcript of the conversation:

        {conversation}

        Here is the job description:

        {self.job_description}
        
        Reference explicitely to the job description should be made in all part of the response.

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

        # overal_assesment = report_content.split("Overall Assessment")[-1].split(
        #     "Final Recommendation"
        # )[0]
        # with open("assets/overall_assesment.txt", "w") as file:
        #     file.write(overal_assesment)

        generate_pdf_report(file_path, report_content)

        return report_content

    def generate_criteria_scores(
        self, conversation: str, file_path: str, criteria: list[str]
    ) -> str:
        """
        Generate a detailed, JSON-formatted evaluation report for the interview based on the provided conversation.

        :param conversation: The interview conversation (questions and answers)
        :param file_path: Path to save the evaluation report
        :param criteria: List of evaluation criteria
        :return: A formatted JSON report as a string.
        """
        prompt = (
            "You are an expert evaluator for interviews. Based on the provided conversation, "
            "evaluate each question in the conversation against the given criteria and assign a score out of 100 for each criterion. "
            "Focus on the specific aspects relevant to each criterion as inferred from the candidate's response to each question. "
            "Ensure the output is in JSON format with the following structure:\n\n"
            "{\n"
            '  "question_scores": [\n'
            "    {\n"
            '      "criteria_scores": [\n'
            "        {\n"
            '          "criterion": "<Name of the Criterion>",\n'
            '          "score": <Numeric Score>,\n'
            "        },\n"
            "        // Continue for all criteria\n"
            "      ]\n"
            "    },\n"
            "    // Continue for all questions\n"
            "  ]\n"
            "}\n\n"
            "Conversation:\n"
            f"{conversation}\n\n"
            "Criteria:\n"
            f"{', '.join(criteria)}\n"
        )

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "assistant", "content": prompt},
            ],
        )
        report_content = (
            response.choices[0]
            .message.content.strip()
            .replace("json", "")
            .replace("```", "")
        )

        # Validate and save the JSON output
        try:
            # Convert the response to JSON for validation
            report_json = json.loads(report_content)
            # with open("assets/overall_assesment.txt", "w") as file:
            #     overall_assesment = file.read()
            generate_short_report(
                scores_dic=report_json,
                filename=file_path,
                overall_assesment="",
            )
            return json.dumps(report_json, indent=4)

        except json.JSONDecodeError as e:
            raise ValueError(
                f"Invalid JSON response: {e}\nResponse Content: {report_content}"
            )
