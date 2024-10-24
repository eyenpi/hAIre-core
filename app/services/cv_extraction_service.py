import os

from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader
from io import BytesIO

def extract_text_from_cv(pdf_bytes):
    # creating a pdf reader object
    reader = PdfReader(BytesIO(pdf_bytes))

    # extracting text
    text = ' '.join([page.extract_text() for page in reader.pages])
    return (text.encode('ascii', 'ignore').decode('ascii').replace('\n', ' '))

def segment_cv(pseudonymized_text):
    load_dotenv()
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    prompt = """
Segment the following text into a JSON format with the fields 'name', 'email', 'work_experiences', and 'educations'. Each work experience should have 'position', 'company', 'from_to' (with dates in 'YYYY-MM-DD to YYYY-MM-DD' or 'YYYY-MM-DD to Present' format), and a 'description'. Each education entry should include 'degree', 'institution', and 'from_to' in the same date format. Ignore fields that are not present and do not add empty keys. Format the final output exactly as specified in the example.
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
    ]
}

return an answer that I can easily decode using json.loads().
**Input text:**
""" + pseudonymized_text
    # print(prompt)

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": prompt}
        ],
    )
    answer = completion.choices[0].message.content
    answer = answer.replace('json', '').replace('```', '')
    # print(answer)
    return answer
