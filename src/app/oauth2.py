from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from fastapi import Depends, status, HTTPException
from datetime import datetime, timedelta

from app.models import TokenData


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = "bc714fc37a3e6f18aa8e3dbce9cb5c9bebf1c7b48fd338472d119d52967a583e"  # any string
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 25


def verify_access_token(token: str, credentials_exception: HTTPException):
    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
        print("!!!", payload)
        id_ = payload.get("user_id")
        is_admin = payload.get("is_admin")
        print("!!!", is_admin)
        if id_ is None:
            raise credentials_exception

        token_data = TokenData(user_id=id_, is_admin=is_admin)
        return token_data
    except JWTError:
        raise credentials_exception


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail=f"Could not validate credentials",
                                          headers={"WWW-Authenticate": "Bearer"})
    return verify_access_token(token, credentials_exception)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    print("???", data)
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})  # this field is optional
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt
