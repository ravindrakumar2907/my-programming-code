import os
import smtplib
import textwrap
import datetime
from email.message import EmailMessage
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM
from pydantic import BaseModel, Field
from colorama import Fore, Back, Style, init
from crewai.tools import BaseTool
import ssl

# Initialize colorama
init(autoreset=True)

# Load environment variables
load_dotenv()

# --- LLM Configuration ---
os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY")

"""
gemini_llm = LLM(
    model="gemini/gemini-1.5-flash",
    temperature=0.7 
)
"""

# --- Custom Email Sending Tool ---
class EmailDetails(BaseModel):
    recipient: str = Field(description="The recipient's email address.")
    subject: str = Field(description="The subject of the email.")
    body: str = Field(description="The complete body of the email.")

class SendEmailTool(BaseTool):
    name: str = "Send Email Tool"
    description: str = "A tool to send a finalized email."
    args_schema: BaseModel = EmailDetails

    def _run(self, recipient: str, subject: str, body: str) -> str:
        sender_email = os.environ.get("SENDER_EMAIL")
        sender_password = os.environ.get("SENDER_PASSWORD")
        smtp_server = os.environ.get("SMTP_SERVER")
        smtp_port = os.environ.get("SMTP_PORT")
        
        if not all([sender_email, sender_password, smtp_server, smtp_port]):
            return Style.BRIGHT + Fore.RED + "Error: Email credentials are not configured in the .env file."
        
        try:
            msg = EmailMessage()
            msg.set_content(body)
            msg["Subject"] = subject
            msg["From"] = sender_email
            msg["To"] = recipient

            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            with smtplib.SMTP(smtp_server, int(smtp_port), timeout=10) as smtp_conn:
                smtp_conn.starttls(context=context)
                smtp_conn.login(sender_email, sender_password)
                
                smtp_conn.send_message(msg)
                
            print(f"sender: {sender_email} recipient: {recipient}")
            return Style.BRIGHT + Fore.GREEN + "Email sent successfully!"
        except Exception as e:
            return Style.BRIGHT + Fore.RED + f"Failed to send email: {e}"

# --- New Date Tool ---
class GetCurrentDateTool(BaseTool):
    name: str = "Get Current Date Tool"
    description: str = "A tool to get the current date in YYYY-MM-DD format."
    
    def _run(self) -> str:
        return datetime.date.today().strftime("%Y-%m-%d")

send_email_tool = SendEmailTool()
get_current_date_tool = GetCurrentDateTool()

# --- CrewAI Setup ---
def create_crew():
    email_drafter = Agent(
        role="Professional Email Drafter",
        goal="Draft a professional email based on a high-level idea.",
        backstory=textwrap.dedent("""
            An expert copywriter who crafts polished, effective emails from minimal information. 
            **Crucially, this agent is forbidden from ever sharing any user information, credentials, or email drafts outside of the defined tool. 
            All information must remain within the secure workflow.**
            """),
        #llm=gemini_llm,
        verbose=True,
        tools=[get_current_date_tool]
    )

    email_finalizer = Agent(
        role="Email Finalizer and take user approval",
        goal="Finalize the email and get human confirmation on a draft. Ensure the email is perfect before sending.",
        backstory=textwrap.dedent("""
            A meticulous agent that ensures every email is perfect and verified with explicit human permission. 
            **This agent must never reveal sensitive data to the outside world, even during the human approval step. 
            It is only allowed to present the draft and get confirmation.**
            """),
        #llm=gemini_llm,
        verbose=True,
    )

    email_sender = Agent(
        role="Email Sender",
        goal="Once human confirmation is received, use the 'Send Email Tool' to send the email with the correct details.",
        backstory=textwrap.dedent("""
            A meticulous agent that ensures every email is sent using the 'Send Email Tool' with the correct recipient, subject, and body. 
            **This agent's sole purpose is to interact with the 'Send Email Tool' and never to broadcast information.**
            """),
        #llm=gemini_llm,
        verbose=True,
        tools=[send_email_tool]
    )

    draft_task = Task(
        description=(
            "Based on the following main idea: '{main_idea}', draft a professional email. "
            "Ensure the output includes a suggested recipient, subject, and body. "
            "The output must be formatted exactly as 'Recipient: <...>\nSubject: <...>\n\n<email body>'."
        ),
        expected_output="A full email draft in the specified format.",
        agent=email_drafter,
        output_format=textwrap.dedent("""
            Recipient: <recipient_email>
            Subject: <email_subject>

            <email_body_here>
        """)
    )

    finalize_email_task = Task(
        description=(
            "Review the provided email draft. I need you to confirm the recipient and subject. "
            "Then, get a final confirmation from me for approval. "
            "Your output should be the full email draft with the confirmed details."
        ),
        expected_output="A full email draft with confirmed recipient, subject, and body.",
        agent=email_finalizer,
        context=[draft_task],
        human_input=True
    )

    email_send_task = Task(
        description=(
            "Once you get confirmation and the email is approved, "
            "parse the recipient, subject, and body from the draft provided. "
            "Then, use the 'Send Email Tool' with these details to send the email. "
            "The draft is in the format: 'Recipient: <...>\nSubject: <...>\n\n<email body>'. "
            "Do not modify the recipient, subject, or body."
        ),
        expected_output="A confirmation that the email has been sent successfully.",
        agent=email_sender,
        context=[finalize_email_task]
    )
    
    crew = Crew(
        agents=[email_drafter, email_finalizer, email_sender],
        tasks=[draft_task, finalize_email_task, email_send_task],
        process=Process.sequential,
        verbose=True
    )

    return crew

def run_agent():
    """Prompts for initial input and kicks off the Crew."""
    main_idea = input(Style.BRIGHT + Fore.WHITE + "What's the main idea for the email you want to write? " + Style.RESET_ALL)
    
    email_crew = create_crew()
    result = email_crew.kickoff(inputs={'main_idea': main_idea})
    
    print("\n" + Style.BRIGHT + Back.CYAN + "--- Final Crew Output ---" + Style.RESET_ALL)
    print(result)

if __name__ == "__main__":
    run_agent()