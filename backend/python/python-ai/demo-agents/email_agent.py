#https://ai.google.dev/gemini-api/docs
from google import genai
import os
import textwrap
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
from colorama import Fore, Back, Style, init

# Initialize colorama to automatically reset color after each print
init(autoreset=True)
global client 

def setup_app():
    try:
        load_dotenv()
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set.")
        client = genai.Client(api_key="YOUR_API_KEY") 
        print(Style.BRIGHT + Back.GREEN +"$$$ Application configured successfully.")
    except Exception as e:
        print(f"" +Style.BRIGHT + Back.GREEN +"$$$ Error during application setup: {e}")
        exit()

def get_initial_input():
    print(Style.BRIGHT + Back.BLUE +"$$$ Welcome! I'm your AI email agent.")
    return input(Style.BRIGHT + Back.WHITE +"$$$ What's the main idea for the email you want to write? ")

def generate_email_draft(main_idea):
    """
    Sends a broad prompt to Gemini to create a full, professional email draft.
    The LLM will infer the recipient and subject.
    """
    prompt = f"""
    ### Role ###
    You are 'The Professional Email Writer', an AI specializing in creating clear, concise, and polite emails.
    Your task is to draft a complete email based on the following main idea.
    You must generate a suitable recipient and subject based on the context provided.

    ### Task ###
    Draft a professional email about the following topic: "{main_idea}"

    ### Output ###
    Provide the email in the following format, including suggested recipient and subject:
    Recipient: <suggested recipient>
    Subject: <suggested subject>

    <Email Body Text Here>
    """
    
    client = genai.Client()
   
    try:
        response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,)
        return response.text
    except Exception as e:
        return f"An error occurred while generating the email: {e}"

def send_email(recipient, subject, body):
    """
    Sends the approved email using a secure SMTP connection.
    """
    sender_email = os.environ.get("SENDER_EMAIL")
    sender_password = os.environ.get("SENDER_PASSWORD")
    smtp_server = os.environ.get("SMTP_SERVER")
    smtp_port = os.environ.get("SMTP_PORT")
    
    if not all([sender_email, sender_password, smtp_server, smtp_port]):
        print(Style.BRIGHT + Back.RED + "Cannot send email: Email credentials are not fully configured in the .env file.")
        return
        
    try:
        msg = EmailMessage()
        msg.set_content(body)
        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = recipient

        with smtplib.SMTP_SSL(smtp_server, int(smtp_port)) as smtp:
            smtp.login(sender_email, sender_password)
            smtp.send_message(msg)
            print(Style.BRIGHT + Back.GREEN +"Email sent successfully!")
            
    except Exception as e:
        print(f"" + Style.BRIGHT + Back.RED + "Failed to send email: {e}")

def main():
    """
    The core loop for the email agent, with a one-step drafting process.
    """
    setup_app()
    main_idea = get_initial_input()

    while True:
        # Generate the draft using only the main idea
        draft = generate_email_draft(main_idea)
        
        # Split the generated text into components
        try:
            lines = draft.strip().split('\n')
            llm_recipient = lines[0].split(': ', 1)[1]
            llm_subject = lines[1].split(': ', 1)[1]
            body = '\n'.join(lines[2:]).strip()
        except IndexError:
            print(Style.BRIGHT + Back.RED +"\nError: The AI response was not in the expected format. Please try again.")
            continue
        
        # Present the draft for verification
        print(Style.BRIGHT + Back.GREEN +"\n--- AI-Generated Email Draft ---")
        print(f"Recipient: {llm_recipient}")
        print(f"Subject: {llm_subject}")
        print("\n" + textwrap.fill(body, width=80))
        print("-------------------------------\n")

        feedback = input(Style.BRIGHT + Back.WHITE +"Does this draft look good? (yes/no/quit): ").lower()

        if feedback in ['yes', 'y']:
            print(Style.BRIGHT + Back.GREEN +"\nDraft approved. Let's get the final details.")
            
            # Final input step before sending
            final_recipient = input(f"Enter the final recipient's email address (or press enter to use '{llm_recipient}'): ") or llm_recipient
            final_subject = input(f"Enter the final subject (or press enter to use '{llm_subject}'): ") or llm_subject
            
            send_confirmation = input("Do you want to send this email now? (yes/no): ").lower()
            if send_confirmation in ['yes', 'y']:
                send_email(final_recipient, final_subject, body)
            else:
                print("Email not sent. Exiting...")
            break
            
        elif feedback in ['no', 'n']:
            print("\nOkay, let's try a different approach. What changes or new ideas should I consider?")
            main_idea = input("Revised idea: ")
            
        elif feedback in ['quit', 'q']:
            print(Style.BRIGHT + Back.GREEN +"$$$ Quitting the program. No email drafted or sent.")
            break
            
        else:
            print(Style.BRIGHT + Back.RED +"$$$ Invalid input. Please respond with 'yes', 'no', or 'quit'.")

if __name__ == "__main__":
    main()