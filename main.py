import os
from datetime import datetime, timedelta, timezone
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from dotenv import load_dotenv
from pwdlib import PasswordHash
from email.mime import application
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, status
from sqlalchemy.orm import Session
from database import ApplicationDB, engine
from typing import Literal

load_dotenv()

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH")
SECRET_KEY = os.getenv("SECRET_KEY")
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
)

password_hash = PasswordHash.recommended()


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:63342"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


security = HTTPBearer()


def require_hr(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    try:
        payload = jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=["HS256"]
        )

        if payload.get("sub") != ADMIN_USERNAME:
            raise HTTPException(
                status_code=401,
                detail="HR ruxsati yo'q"
            )

        return payload["sub"]

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Token yaroqsiz yoki muddati tugagan"
        )


@app.get("/")
def forma():
    return {"message": "HR Application API ishlayapti"}


@app.get("/forma")
def hr_forma():
    return {"message": "Ishga ariza topshirish formasi"}


class Application(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: str
    gender: str
    citizenship: str
    residential_address: str
    phone_number: str
    email: str



@app.post("/applications")
def create_application(application: Application):
    with Session(engine) as session:
        new_application = ApplicationDB(
            first_name=application.first_name,
            last_name=application.last_name,
            date_of_birth=application.date_of_birth,
            gender=application.gender,
            citizenship=application.citizenship,
            residential_address=application.residential_address,
            phone_number=application.phone_number,
            email=application.email,
        )

        session.add(new_application)
        session.commit()
        session.refresh(new_application)

        return {
            "message": "Ariza muvaffaqiyatli saqlandi",
            "application_id": new_application.id,
        }


@app.get("/applications")
def get_applications(status:Literal["pending", "approved", "rejected"] | None=None,first_name: str | None = None,hr: str = Depends(require_hr)):
    with Session(engine) as session:
        if status is not None and first_name is not None:
            # Ikkala parametr ham berilgan
            applications =session.query(ApplicationDB).filter(ApplicationDB.status == status, ApplicationDB.first_name == first_name).all()
        elif status is not None and first_name is None:
            applications = session.query(ApplicationDB).filter(ApplicationDB.status == status).all()
        elif first_name is not None and status is None:
            applications = session.query(ApplicationDB).filter(ApplicationDB.first_name == first_name).all()
        else:
            applications = session.query(ApplicationDB).all()

        return [
            {
                "id": app.id,
                "first_name": app.first_name,
                "last_name": app.last_name,
                "date_of_birth": app.date_of_birth,
                "gender": app.gender,
                "citizenship": app.citizenship,
                "residential_address": app.residential_address,
                "phone_number": app.phone_number,
                "email": app.email,
                "status": app.status,
            }
            for app in applications
        ]




@app.get("/applications/{application_id}")
def get_application(application_id: int):
    with Session(engine) as session:
        application = session.get(ApplicationDB, application_id)

        if application is None:
            raise HTTPException(
                status_code=404,
                detail="Ariza topilmadi!"
            )

        return {
            "id": application.id,
            "first_name": application.first_name,
            "last_name": application.last_name,
            "date_of_birth": application.date_of_birth,
            "gender": application.gender,
            "citizenship": application.citizenship,
            "residential_address": application.residential_address,
            "phone_number": application.phone_number,
            "email": application.email,
        }

@app.delete("/applications/{application_id}")
def delete_application(application_id: int):
    with Session(engine) as session:
        application = session.get(ApplicationDB, application_id)

        if application is None:
            raise HTTPException(
                status_code=404,
                detail="Ariza topilmadi!"
            )

        session.delete(application)
        session.commit()

        return {
            "message": "Ariza muvaffaqiyatli o'chirildi",
            "application_id": application_id
        }
class ApplicationStatusUpdate(BaseModel):
    status: Literal["pending", "approved", "rejected"]

@app.patch("/applications/{application_id}/status")
def update_application_status(
    application_id: int,
    data: ApplicationStatusUpdate):
    with Session(engine) as session:
        application = session.get(ApplicationDB, application_id)

        if application is None:
            raise HTTPException(
                status_code=404,
                detail="Ariza topilmadi!"
            )

        application.status = data.status
        session.commit()
        session.refresh(application)

        return {
            "message": "Ariza holati yangilandi",
            "application_id": application.id,
            "status": application.status
        }

class HRLogin(BaseModel):
    username: str
    password: str

@app.post("/hr/login")
def hr_login(data: HRLogin):
    if not ADMIN_USERNAME or not ADMIN_PASSWORD_HASH or not SECRET_KEY:
        raise HTTPException(
            status_code=500,
            detail="HR tizimi sozlanmagan"
        )

    if data.username != ADMIN_USERNAME:
        raise HTTPException(
            status_code=401,
            detail="Login yoki parol noto‘g‘ri"
        )

    if not password_hash.verify(
        data.password,
        ADMIN_PASSWORD_HASH
    ):
        raise HTTPException(
            status_code=401,
            detail="Login yoki parol noto‘g‘ri"
        )

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    token = jwt.encode(
        {
            "sub": ADMIN_USERNAME,
            "exp": expire
        },
        SECRET_KEY,
        algorithm="HS256"
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }

