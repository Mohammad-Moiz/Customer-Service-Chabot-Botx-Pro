"""Dependency of product"""

from fastapi import HTTPException
from sqlalchemy.orm import Session

from configuration import constants
from features.contact_us.models import ContactFormModel
from features.contact_us.schemas import ContactForm
from utilities.email.main_email import send_contactus_email


def submit_contact_form(db: Session, contact_data: ContactForm) -> dict:
    try:
        # Extract data from the contact form
        name = contact_data.name
        email = contact_data.email
        subject = contact_data.subject
        message = contact_data.message

        # Create a new instance of ContactFormModel
        new_contact_form = ContactFormModel(
            name=name, email=email, subject=subject, message=message
        )

        # Add the new contact form to the session and commit changes
        db.add(new_contact_form)
        db.commit()

        # Refresh the instance to get the updated data from the database
        db.refresh(new_contact_form)
        send_contactus_email(email, name)

        # Return success response with the saved contact form data
        return {
            "status": True,
            "message": constants.CONTACT_FORM,
            "data": {
                "id": new_contact_form.id,
                "name": new_contact_form.name,
                "email": new_contact_form.email,
                "subject": new_contact_form.subject,
                "message": new_contact_form.message,
            },
        }
    except HTTPException:
        return HTTPException(
            status_code=400,
            detail={
                "status": False,
                "message": constants.CONTACT_FORM_FAIL,
            },
        )
