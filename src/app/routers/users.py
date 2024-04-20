from fastapi import APIRouter, HTTPException, status, Response, Depends
from fastapi.responses import JSONResponse
import random
from sqlalchemy.orm import Session

from app.models import UserBody, TokenData
from db.orm import get_session
from db.models import UserTable
from app import oauth2


router = APIRouter()


@router.get("/users/", tags=["users"])
def get_users(session: Session = Depends(get_session),
              user_data: TokenData = Depends(oauth2.get_current_user)):
    if not user_data.is_admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Only admin can perform this operation")

    users_data = session.query(UserTable).all()
    # return JSONResponse(status_code=status.HTTP_200_OK, content={"result": users_data})
    return {"result": users_data}


@router.get("/users/{id_}", tags=["users"])
def get_user_by_id(id_: int, session: Session = Depends(get_session),
                   user_data: TokenData = Depends(oauth2.get_current_user)):
    if not user_data.is_admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Only admin can perform this operation")

    target_user = session.query(UserTable).filter_by(id_number=id_).first()

    if not target_user:
        message = {"error": f"User with id {id_} does not exist"}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)

    return {"result": target_user}


@router.post("/users/", status_code=status.HTTP_201_CREATED, tags=["users"])
def create_user(body: UserBody, session: Session = Depends(get_session)):
    user_dict = body.model_dump()
    new_user = UserTable(**user_dict)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return {"message": "New user added", "details": new_user}


@router.delete("/users/{id_}", tags=["users"])
def delete_user_by_id(id_: int, session: Session = Depends(get_session),
                      user_data: TokenData = Depends(oauth2.get_current_user)):
    if not (user_data.is_admin or user_data.user_id == id_):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="You are not authorized to perform this operation")

    deleted_user = session.query(UserTable).filter_by(id_number=id_).first()

    if deleted_user is None:
        message = {"error": f"User with id {id_} does not exist"}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)

    session.delete(deleted_user)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/users/{id_}", tags=["users"])
def update_user_by_id(id_: int, body: UserBody, session: Session = Depends(get_session),
                      show_user: bool = True, user_data: TokenData = Depends(oauth2.get_current_user)):
    if not (user_data.is_admin or user_data.user_id == id_):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="You are not authorized to perform this operation")

    filter_query = session.query(UserTable).filter_by(id_number=id_)

    if filter_query.first() is None:
        message = {"error": f"User with id {id_} does not exist"}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)

    filter_query.update(body.model_dump())
    session.commit()

    updated_user = filter_query.first()

    if show_user:
        return {"message": f"User with id {id_} updated", "new_value": updated_user}
    else:
        return {"message": f"User with id {id_} updated"}
