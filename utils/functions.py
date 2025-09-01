from typing import Any
from sqlalchemy.orm import (
    Mapped,
    MappedColumn,
    mapped_column as column,
    relationship,
)
from sqlalchemy import CheckConstraint as constraint, ForeignKey as fk, Integer


def defaultPrimaryKey() -> Mapped[int]:
    return column(Integer, autoincrement=True, primary_key=True)


def positive(column_name: str) -> MappedColumn[Any]:
    name = column_name
    return column(constraint(f"{name} >= 0", name=f"check_{name}"))


def backref(back_populates: str) -> Mapped[Any]:
    return relationship(back_populates=back_populates)


def childOf(back_populates: str) -> Mapped[Any]:
    return relationship(
        back_populates=back_populates,
        cascade="all, delete-orphan",
    )


def foreignKeyCascade(foreign_key: str) -> MappedColumn[Any]:
    return column(fk(foreign_key, ondelete="CASCADE"))
