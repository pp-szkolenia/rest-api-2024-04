from fastapi import APIRouter, HTTPException, status, Response, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy import func, asc, desc
from sqlalchemy.orm import Session

from app.models import UserBody, SortOrders
from db.orm import get_session
from db.models import UserTable


router = APIRouter()


@router.get("/users/", tags=["users"])
def get_users(request: Request, session: Session = Depends(get_session), is_admin: bool | None = None,
              password_limit: int = None, sort_username: SortOrders = None):

    print("!!!", request.headers, "\n--------")

    users_data = session.query(UserTable)

    if is_admin is not None:
        users_data = users_data.filter_by(is_admin=is_admin)

    if password_limit is not None:
        users_data = users_data.filter(func.length(UserTable.password) <= password_limit)

    if sort_username is not None:
        if sort_username == SortOrders.ASC:
            sort_func = asc
        elif sort_username == SortOrders.DESC:
            sort_func = desc
        else:
            raise Exception("Invalid sort order")

        users_data = users_data.order_by(sort_func(UserTable.username))

    users_data = users_data.all()

    users_data = [
        {"id": user.id_number,
         "username": user.username,
         "password": user.password,
         "is_admin": user.is_admin}
        for user in users_data]

    return {"result": users_data}


@router.get("/users/{id_}", tags=["users"])
def get_user_by_id(id_: int, session: Session = Depends(get_session)):
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
def delete_user_by_id(id_: int, session: Session = Depends(get_session)):
    deleted_user = session.query(UserTable).filter_by(id_number=id_).first()

    if deleted_user is None:
        message = {"error": f"User with id {id_} does not exist"}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)

    session.delete(deleted_user)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/users/{id_}", tags=["users"])
def update_user_by_id(id_: int, body: UserBody, session: Session = Depends(get_session)):
    filter_query = session.query(UserTable).filter_by(id_number=id_)

    if filter_query.first() is None:
        message = {"error": f"User with id {id_} does not exist"}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)

    filter_query.update(body.model_dump())
    session.commit()

    updated_user = filter_query.first()

    message = {"message": f"User with id {id_} updated", "new_value": updated_user}
    # return JSONResponse(status_code=status.HTTP_200_OK, content=message)
    return message
