import email.mime.text as mime
import smtplib
import ssl
from email.mime import multipart
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from fastapi import HTTPException

from configuration import constants
from configuration.configure import sender_email, sender_password
from configuration.constants import PROJECT_TITLE
from features.order.models import OrderModel


def gmail_html_email_sender(
    username: str,
    db_otp: str,
    receiver_email: str,
    email_template: str,
) -> None:
    file_location = "utilities/email/custom_emails/" + email_template + ".html"
    with open(
        file_location,
        "r",
        encoding="utf-8",
    ) as file:
        html_content = file.read()
        context = ssl.create_default_context()
        smtp_server = smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context)
        smtp_server.login(sender_email, sender_password)
        msg = multipart.MIMEMultipart()
        html_part = mime.MIMEText(
            html_content.format(
                username=username, otp=db_otp, receiver_email=receiver_email
            ),
            "html",
        )
        msg.attach(html_part)
        msg["Subject"] = "OTP verification"
        msg["From"] = PROJECT_TITLE + " <" + sender_email + ">"
        msg["To"] = receiver_email
        smtp_server.sendmail(sender_email, receiver_email, msg.as_string())
        smtp_server.quit()


def gmail_order_email_sender(
    username: str,
    order: OrderModel,
    receiver_email: str,
    email_template: str,
) -> None:
    file_location = "utilities/email/custom_emails/" + email_template + ".html"
    with open(
        file_location,
        "r",
        encoding="utf-8",
    ) as file:
        html_content = file.read()
        context = ssl.create_default_context()
        smtp_server = smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context)
        smtp_server.login(sender_email, sender_password)
        msg = multipart.MIMEMultipart()
        html_part = mime.MIMEText(
            html_content.format(
                username=username, order=order.name, quantity=order.quantity, receiver_email=receiver_email
            ),
            "html",
        )
        msg.attach(html_part)
        msg["Subject"] = "Your Order"
        msg["From"] = PROJECT_TITLE + " <" + sender_email + ">"
        msg["To"] = receiver_email
        smtp_server.sendmail(sender_email, receiver_email, msg.as_string())
        smtp_server.quit()
        print(f"Email send: {username} - {order.name} - {order.price}")


def send_email(to_email: str,full_name:str,product: str) -> dict:
    
    
    try:

        email_template = "promotion_email_template"
        file_location = "utilities/email/custom_emails/" + email_template + ".html"
        with open(
            file_location,
            "r",
            encoding="utf-8",
        ) as file:
            html_content = file.read()
            context = ssl.create_default_context()
            smtp_server = smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context)
            smtp_server.login(sender_email, sender_password)
            msg = multipart.MIMEMultipart()
            html_part = mime.MIMEText(
                html_content.format(username=full_name,receiver_email=to_email,product=product),
                "html",
            )
            msg.attach(html_part)
            msg["Subject"] = "Promotion Product"
            msg["From"] = PROJECT_TITLE + " <" + sender_email + ">"
            msg["To"] = to_email
            smtp_server.sendmail(sender_email, to_email, msg.as_string())
            smtp_server.quit()

        # return {
        #     "status": True,
        #     "message": constants.EMAIL_SENT,
        # }
    

    except HTTPException:
        return HTTPException(
            status_code=400,
            detail={
                "status": False,
                "message": constants.SOMETHING_WRONG,
            },
        )

   
    
  
    # if 'arshadshiwani990@gmail.com' in to_email:
    #     print(to_email)
    #     email_template = "promotion_email_template"
    #     file_location = "utilities/email/custom_emails/" + email_template + ".html"
    #     with open(
    #         file_location,
    #         "r",
    #         encoding="utf-8",
    #     ) as file:
    #         html_content = file.read()
    #         context = ssl.create_default_context()
    #         smtp_server = smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context)
    #         smtp_server.login(sender_email, sender_password)
    #         msg = multipart.MIMEMultipart()
    #         html_part = mime.MIMEText(
    #             html_content.format(product='test'),
    #             "html",
    #         )
    #         msg.attach(html_part)
    #         msg["Subject"] = "Thank you for contact us"
    #         msg["From"] = PROJECT_TITLE + " <" + sender_email + ">"
    #         msg["To"] = to_email
    #         smtp_server.sendmail(sender_email, to_email, msg.as_string())
    #         smtp_server.quit()
    
    


def send_contactus_email(receiver_email: str, name: str) -> None:
    email_template = "contact_us_templete"
    file_location = "utilities/email/custom_emails/" + email_template + ".html"
    with open(
        file_location,
        "r",
        encoding="utf-8",
    ) as file:
        html_content = file.read()
        context = ssl.create_default_context()
        smtp_server = smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context)
        smtp_server.login(sender_email, sender_password)
        msg = multipart.MIMEMultipart()
        html_part = mime.MIMEText(
            html_content.format(username=name, receiver_email=receiver_email),
            "html",
        )
        msg.attach(html_part)
        msg["Subject"] = "Thank you for contact us"
        msg["From"] = PROJECT_TITLE + " <" + sender_email + ">"
        msg["To"] = receiver_email
        smtp_server.sendmail(sender_email, receiver_email, msg.as_string())
        smtp_server.quit()
