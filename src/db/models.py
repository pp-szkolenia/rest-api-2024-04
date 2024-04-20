from sqlalchemy import Column, Integer, Boolean, VARCHAR
from sqlalchemy.sql.expression import false

from db.orm import Base


class UserTable(Base):
    __tablename__ = "users"

    id_number = Column("id", Integer, primary_key=True)
    username = Column("username", VARCHAR(20), nullable=False)
    password = Column("password", VARCHAR(30), nullable=False)
    is_admin = Column("is_admin", Boolean, nullable=False, server_default=false())

    def __repr__(self):
        return f"User(id={self.id_number}"


class TaskTable(Base):
    __tablename__ = "tasks"

    id_number = Column("id", Integer, primary_key=True)
    description = Column("description", VARCHAR(30), nullable=False)
    priority = Column("priority", Integer)
    is_complete = Column("is_complete", Boolean, nullable=False, server_default=false())
