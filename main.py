"""Starting point of app"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from uvicorn import run

import configuration.constants as appConst
from configuration import configure
from db.db_setup import Base, engine
from features.authentication.users.routes import userAuth
from features.authentication.vendor.routes import vendorAuth
from features.chatbot.web_chatbot.routers import chat_bot
from features.chatbot.whatsapp_bot.routers import whatsapp_chatbot
from features.contact_us.routes import contactus
from features.order.routes import order
from features.product.routes import product
from features.promotion.routes import promotion
from features.users_data.routes import user_data

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=appConst.PROJECT_TITLE,
    description=appConst.PROJECT_DESCRIPTION,
    version=appConst.PROJECT_VERSION,
    contact=appConst.contactInfo,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=configure.origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(userAuth)
app.include_router(vendorAuth)
app.include_router(product)
app.include_router(order)
app.include_router(chat_bot)
app.include_router(whatsapp_chatbot)
app.include_router(user_data)
app.include_router(promotion)
app.include_router(contactus)


if __name__ == "__main__":
    run(app, host="0.0.0.0", port=8000)
