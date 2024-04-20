from passlib.context import CryptContext

# from app.models import UserBody


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify(login_password: str, true_password: str):
    # return pwd_context.verify(raw_password, hashed_password)
    return login_password == true_password
