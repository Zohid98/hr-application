
from sqlalchemy import create_engine,Integer, String
from sqlalchemy import text
from sqlalchemy.engine import URL
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import mapped_column
DATABASE_URL = URL.create(
    drivername="postgresql+psycopg",
    username="postgres",
    password="yangi_parol123",
    host="localhost",
    port=5432,
    database="hr_app",
)

engine = create_engine(DATABASE_URL)

Base = declarative_base()


class ApplicationDB(Base):
    __tablename__ = "applications"

    id = mapped_column(Integer, primary_key=True, index=True)
    first_name = mapped_column(String(100), nullable=False)
    last_name = mapped_column(String(100), nullable=False)
    date_of_birth = mapped_column(String(20), nullable=False)
    gender = mapped_column(String(30), nullable=False)
    citizenship = mapped_column(String(100), nullable=False)
    residential_address = mapped_column(String(300), nullable=False)
    phone_number = mapped_column(String(30), nullable=False)
    email = mapped_column(String(150), nullable=False)
    status = mapped_column(String(20), nullable=False, default="pending")
    status = mapped_column(
        String(20),
        nullable=False,
        default="pending"
    )

Base.metadata.create_all(engine)

print("Applications jadvali yaratildi!")


try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print("PostgreSQL bilan ulanish muvaffaqiyatli!")
        print("Natija:", result.scalar())

except Exception as e:
    print("Ulanishda xato yuz berdi:", e)
