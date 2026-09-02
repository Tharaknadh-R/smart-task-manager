from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base

class IDCounter(Base):
    __tablename__ = "id_counters"

    id: Mapped[int] = mapped_column( primary_key=True, autoincrement=True)
    entity: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    value: Mapped[int] = mapped_column(Integer, nullable=False, default=0)