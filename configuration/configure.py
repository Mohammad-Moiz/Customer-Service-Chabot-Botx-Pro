"""Config file of app."""
import os

from dotenv import load_dotenv

load_dotenv()

dbConnectionUrl = os.getenv("DATABASE_URL")
dbAsyncConnectionUrl = os.getenv("ASYNC_DATABASE_URL")
sender_email = os.getenv("SENDER_EMAIL")
sender_password = os.getenv("SENDER_EMAIL_PASS")
openai_api_key = os.getenv("OPENAI_API_KEY")
whatsapp_access_token = os.getenv("ACCESS_TOKEN")
phone_number_id = os.getenv("PHONE_NUMBER_ID")
meta_version = os.getenv("VERSION")
webhook_verify_token = os.getenv("WEBHOOK_VERIFY_TOKEN")
port=  os.getenv("PORT")
origins = [
    "*",
    os.getenv("FRONTEND_ORIGIN_1"),
    os.getenv("FRONTEND_ORIGIN_2"),
]
FB_graph_token=os.getenv("FB_graph_token")