"""Authentication routes for api."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.db_setup import get_db
from features.contact_us.dependency import submit_contact_form
from features.contact_us.schemas import ContactForm

# from utilities.module_utils import get_user_role

contactus = APIRouter()


@contactus.post("/contact/contact_us", tags=["Contact_Us"])
def contact_us_endpoint(
    contactus_data: ContactForm, db: Session = Depends(get_db)
) -> dict:
    submission_result = submit_contact_form(db=db, contact_data=contactus_data)
    return submission_result
