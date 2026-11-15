from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SqlEnum, Float, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class GameStatus(str, Enum):
    backlog = "backlog"
    playing = "playing"
    completed = "completed"
    dropped = "dropped"


class LinuxCompat(str, Enum):
    native = "native"
    proton = "proton"
    windows_only = "windows_only"
    unknown = "unknown"


def enum_values(enum_class: type[Enum]) -> list[str]:
    return [member.value for member in enum_class]


class Game(Base):
    __tablename__ = "games"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    platform: Mapped[str] = mapped_column(String(50), nullable=False)
    genre: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[GameStatus] = mapped_column(
        SqlEnum(GameStatus, values_callable=enum_values, name="game_status"),
        default=GameStatus.backlog,
        nullable=False,
    )
    hours_played: Mapped[float] = mapped_column(
        Float, default=0.0, nullable=False
    )
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    linux_compat: Mapped[LinuxCompat] = mapped_column(
        SqlEnum(LinuxCompat, values_callable=enum_values, name="linux_compat"),
        default=LinuxCompat.unknown,
        nullable=False,
    )
    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
