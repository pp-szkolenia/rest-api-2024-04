from fastapi import APIRouter, HTTPException, status, Response, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import between, asc, desc

from sqlalchemy.orm import Session
from db.orm import get_session
from app.models import TaskBody, SortOrders
from db.utils import connect_to_db
from db.models import TaskTable


router = APIRouter()


@router.get("/tasks/", tags=["tasks"])
def get_tasks(session: Session = Depends(get_session), is_complete: bool | None = None,
              min_priority: int = 1, max_priority: int = 5, sort_description: SortOrders = None):
    tasks_data = session.query(TaskTable)

    if is_complete is not None:
        tasks_data = tasks_data.filter_by(is_complete=is_complete)

    tasks_data = tasks_data.filter(between(TaskTable.priority, min_priority, max_priority))

    if sort_description is not None:
        if sort_description == SortOrders.ASC:
            sort_func = asc
        elif sort_description == SortOrders.DESC:
            sort_func = desc
        else:
            raise Exception("Invalid sort order")

        tasks_data = tasks_data.order_by(sort_func(TaskTable.description))

    tasks_data = tasks_data.all()

    tasks_data = [{
        "id": task.id_number,
        "description": task.description,
        "priority": task.priority,
        "is_complete": task.is_complete,
    }
        for task in tasks_data]

    return {"result": tasks_data}


@router.get("/tasks/{id_}", tags=["tasks"])
def get_task_by_id(id_: int, session: Session = Depends(get_session)):
    target_task = session.query(TaskTable).filter_by(id_number=id_).first()

    if not target_task:
        message = {"error": f"Task with id {id_} does not exist"}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)

    target_task = {"id": target_task.id_number,
                   "description": target_task.description,
                   "priority": target_task.priority,
                   "is_complete": target_task.is_complete}

    return {"result": target_task}


@router.post("/tasks/", status_code=status.HTTP_201_CREATED, tags=["tasks"])
def create_task(body: TaskBody):
    conn, cursor = connect_to_db()

    insert_query_template = f"""INSERT INTO tasks (description, priority, is_complete)
                                VALUES (%s, %s, %s) RETURNING *;"""
    insert_query_values = (body.description, body.priority, body.is_complete)

    cursor.execute(insert_query_template, insert_query_values)
    new_task = cursor.fetchone()
    conn.commit()

    conn.close()
    cursor.close()

    return {"message": "New task added", "details": new_task}


@router.delete("/tasks/{id_}", tags=["tasks"])
def delete_task_by_id(id_: int):
    conn, cursor = connect_to_db()

    delete_query = f"DELETE FROM tasks WHERE id=%s RETURNING *;"
    cursor.execute(delete_query, (id_,))
    deleted_post = cursor.fetchone()
    conn.commit()

    conn.close()
    cursor.close()

    if deleted_post is None:
        message = {"error": f"Task with id {id_} does not exist"}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/tasks/{id_}", tags=["tasks"])
def update_task_by_id(id_: int, body: TaskBody):
    conn, cursor = connect_to_db()

    update_query = (f"""UPDATE tasks SET description=%s, priority=%s, is_complete=%s
                        WHERE id=%s RETURNING *;""")
    update_values = (body.description, body.priority, body.is_complete, id_)

    cursor.execute(update_query, update_values)
    updated_task = cursor.fetchone()
    conn.commit()

    conn.close()
    cursor.close()

    if updated_task is None:
        message = {"error": f"Task with id {id_} does not exist"}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)

    message = {"message": f"Task with id {id_} updated", "new_value": updated_task}
    return JSONResponse(status_code=status.HTTP_200_OK, content=message)
