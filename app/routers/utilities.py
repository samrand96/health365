from app.helpers.mail import send_mail as mail
from app.helpers.security import oauth2_scheme
from fastapi import APIRouter, Depends

router = APIRouter()


@router.post('/send-mail')
async def send_mail(email: str, subject: str, content: str,
                    token: str = Depends(oauth2_scheme)):
    """
        Async function to send an email with the given email, subject, and content.

        Parameters:
            email (str): The email address to send the mail to.
            subject (str): The subject of the email.
            content (str): The content/body of the email.
            token (str): The OAuth2 token for authorization.

        Returns:
            The status code of the email sending response.
    """
    response = mail(email, subject, content)
    return response.status_code
