from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models import GameStatus, LinuxCompat


class GameBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=150)
    platform: str = Field(min_length=1, max_length=50)
    genre: str | None = Field(default=None, max_length=50)
    status: GameStatus = GameStatus.backlog
    hours_played: float = Field(default=0.0, ge=0)
    rating: int | None = Field(default=None, ge=1, le=10)
    linux_compat: LinuxCompat = LinuxCompat.unknown
    notes: str | None = Field(default=None, max_length=1000)


class GameCreate(GameBase):
    pass


class GameUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str | None = Field(default=None, min_length=1, max_length=150)
    platform: str | None = Field(default=None, min_length=1, max_length=50)
    genre: str | None = Field(default=None, max_length=50)
    status: GameStatus | None = None
    hours_played: float | None = Field(default=None, ge=0)
    rating: int | None = Field(default=None, ge=1, le=10)
    linux_compat: LinuxCompat | None = None
    notes: str | None = Field(default=None, max_length=1000)


class GameRead(GameBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class StatsSummary(BaseModel):
    total_games: int
    total_hours: float
    average_rating: float | None


class GenreStats(BaseModel):
    genre: str
    total_games: int
    total_hours: float


class LinuxCompatStats(BaseModel):
    linux_compat: LinuxCompat
    total_games: int
    percentage: float
