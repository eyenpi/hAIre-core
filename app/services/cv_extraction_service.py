import os
from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader
from io import BytesIO


class CVProcessor:
    def __init__(self, openai_api_key: str = None):
        # Load OpenAI API key from environment if not provided
        self.api_key = openai_api_key
        self.client = OpenAI(api_key=self.api_key)

    @staticmethod
    def extract_text_from_cv(pdf_filename) -> str:
        """
        Extracts text from a PDF file in bytes format.

        Args:
            pdf_bytes (bytes): PDF content as bytes.

        Returns:
            str: Extracted text from the PDF, cleaned and formatted.
        """
        reader = PdfReader(pdf_filename)
        text = "\n\n\n".join([page.extract_text() for page in reader.pages])
        cleaned_text = text.encode("ascii", "ignore").decode("ascii")
        return cleaned_text

    def segment_cv(self, pseudonymized_text: str) -> str:
        """
        Segments CV text into structured JSON format using OpenAI API.

        Args:
            pseudonymized_text (str): Pseudonymized text of the CV.

        Returns:
            str: Segmented JSON formatted text.
        """
        prompt = (
            """
        Segment the following text into a JSON format with the fields 'name', 'email', 'work_experiences', and 'educations'. Each work experience should have 'position', 'company', 'from_to' (with dates in 'YYYY-MM-DD to YYYY-MM-DD' or 'YYYY-MM-DD to Present' format), and a 'description'. Each education entry should include 'degree', 'institution', and 'from_to' in the same date format. Ignore fields that are not present and do not add empty keys. Format the final output exactly as specified in the example.
        *Example output:*

        {{
            "name": "Hosein",
            "email": "hoseinmirhoseini64@gmail.com",
            "work_experiences": [
                {{
                    "position": "Software Engineer",
                    "company": "Scalapay",
                    "from_to": "2021-01-01 to Present",
                    "description": "Software Engineer at Scalapay"
                }},
                {{
                    "position": "Frontend Developer",
                    "company": "Apple",
                    "from_to": "2020-01-01 to 2021-01-01",
                    "description": "Frontend Developer at Apple"
                }}
            ],
            "educations": [
                {{
                    "degree": "Bachelor of Computer Science",
                    "institution": "Shiraz University",
                    "from_to": "2017-01-01 to 2021-09-01"
                }}
            ]
        }}

        return an answer that I can easily decode using json.loads().
        **Input text:**
        """
            + pseudonymized_text
        )

        completion = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
        )
        answer = completion.choices[0].message.content
        answer = answer.replace("json", "").replace("```", "")
        return answer
