from openai import OpenAI
from pypdf import PdfReader
import pdfplumber
import re


class CVProcessor:
    def __init__(self, openai_api_key: str = None):
        # Load OpenAI API key from environment if not provided
        self.api_key = openai_api_key
        self.client = OpenAI(api_key=self.api_key)

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Cleans the extracted text by removing unnecessary spaces,
        non-printable characters, and correcting common OCR errors.

        Args:
            text (str): Raw extracted text.

        Returns:
            str: Cleaned text.
        """
        # Remove non-printable characters
        text = re.sub(r"[^\x20-\x7E\n]", "", text)

        # Replace multiple spaces/newlines with a single instance
        text = re.sub(r"\s+", " ", text).strip()

        return text

    @staticmethod
    def extract_text_from_cv(pdf_filename: str) -> str:
        """
        Extracts text from a PDF file.

        Args:
            pdf_filename (str): Path to the PDF file.

        Returns:
            str: Cleaned and formatted text extracted from the PDF.
        """
        try:
            # Use pdfplumber for more accurate text extraction
            with pdfplumber.open(pdf_filename) as pdf:
                pages = [
                    page.extract_text() for page in pdf.pages if page.extract_text()
                ]

            if not pages:  # Fallback if pdfplumber fails
                reader = PdfReader(pdf_filename)
                pages = [page.extract_text() for page in reader.pages]

            # Join extracted text from all pages
            raw_text = "\n\n".join(pages)

            # Clean the extracted text
            cleaned_text = CVProcessor.clean_text(raw_text)
            return cleaned_text

        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")

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
            Segment the following text into a JSON format with the fields 'name', 'email', 'work_experiences', 'educations', and 'skills'. Each work experience should have 'position', 'company', 'from_to' (with dates in 'YYYY to YYYY' or 'YYYY to Present' format), and a 'description'. Each education entry should include 'degree', 'institution', and 'from_to' in the same date format. 'Skills' should be an array of relevant skills mentioned in the text. Ignore fields that are not present and do not add empty keys. Format the final output exactly as specified in the example.

            *Example output:*

            {
                "name": "Hosein",
                "email": "hoseinmirhoseini64@gmail.com",
                "work_experiences": [
                    {
                        "position": "Software Engineer",
                        "company": "Scalapay",
                        "from_to": "2021-01-01 to Present",
                        "description": "Software Engineer at Scalapay"
                    },
                    {
                        "position": "Frontend Developer",
                        "company": "Apple",
                        "from_to": "2020-01-01 to 2021-01-01",
                        "description": "Frontend Developer at Apple"
                    }
                ],
                "educations": [
                    {
                        "degree": "Bachelor of Computer Science",
                        "institution": "Shiraz University",
                        "from_to": "2017-01-01 to 2021-09-01"
                    }
                ],
                "skills": ["Python", "JavaScript", "Problem Solving"]
            }
            
            Return an answer that I can easily decode using json.loads().
            
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
