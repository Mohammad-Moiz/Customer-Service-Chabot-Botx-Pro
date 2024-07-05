from pydantic import BaseModel


class ContactForm(BaseModel):
    name: str
    email: str
    subject: str
    message: str
