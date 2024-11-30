import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class EmailSender:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER")
        self.smtp_port = int(
            os.getenv("SMTP_PORT", 587)
        )  # Default to 587 if not in .env
        self.username = os.getenv("SMTP_USERNAME")
        self.password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("FROM_EMAIL")

    def send_email(
        self, to_email: str, subject: str, body: str, file_paths: list = None
    ):
        # Create the email message
        msg = MIMEMultipart()
        msg["From"] = self.from_email
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        # Attach the file if provided
        for file_path in file_paths:
            if file_path:
                self.attach_file(msg, file_path)

        # Send the email using the SMTP server
        try:
            # Connect to the SMTP server
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()  # Upgrade the connection to a secure encrypted SSL/TLS connection

            # Login to the SMTP server
            server.login(self.username, self.password)

            # Send the email
            server.sendmail(self.from_email, to_email, msg.as_string())

            # Close the connection
            server.quit()
            print("Email with attachment sent successfully!")
        except Exception as e:
            print(f"Failed to send email. Error: {str(e)}")

    def attach_file(self, msg: MIMEMultipart, file_path: str):
        """Attach a file to the email."""
        filename = os.path.basename(file_path)  # Get the file name
        try:
            with open(file_path, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename= {filename}",
                )
                msg.attach(part)
        except Exception as e:
            print(f"Could not attach file. Error: {str(e)}")
