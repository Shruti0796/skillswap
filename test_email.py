from dotenv import load_dotenv
from app.utils.email_utils import send_email

load_dotenv()

result = send_email(
    "shankleshashruti200@gmail.com",
    "SkillSwap Resend Test",
    """
    <h1>SkillSwap Email Test</h1>
    <p>If you received this, Resend is working correctly.</p>
    """
)

print("Resend response:")
print(result)