from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from app.helpers.constant import FROM_EMAIL, SENDGRID_API_KEY

SENDGRID_CLIENT = SendGridAPIClient(SENDGRID_API_KEY)


def send_mail(to_email, subject, html_content):
    """
        Sends an email message to the specified email address with the given subject and HTML content.

        Parameters:
            - to_email (str): The email address to send the email to.
            - subject (str): The subject of the email.
            - html_content (str): The HTML content/body of the email.

        Returns:
            - The response from sending the email.
    """
    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=to_email,
        subject=subject,
        html_content=html_content
    )
    try:
        response = SENDGRID_CLIENT.send(message)

        # log response
        print(response.status_code)
        print(response.body)
        print(response.headers)

        return response

    except Exception as e:
        print(e.message)