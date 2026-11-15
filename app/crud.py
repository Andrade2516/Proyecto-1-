from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Game, GameStatus, LinuxCompat
from app.schemas import GameCreate, GameUpdate

CLEARABLE_FIELDS = {"genre", "rating", "notes"}


def create_game(db: Session, game_in: GameCreate) -> Game:
    game = Game(**game_in.model_dump())
    db.add(game)
    db.commit()
    db.refresh(game)
    return game


def get_game(db: Session, game_id: int) -> Game | None:
    return db.get(Game, game_id)


def get_all_games(db: Session) -> list[Game]:
    statement = select(Game).order_by(Game.id)
    return list(db.scalars(statement).all())


def get_games(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    status: GameStatus | None = None,
    genre: str | None = None,
    linux_compat: LinuxCompat | None = None,
) -> list[Game]:
    statement = select(Game)

    if status is not None:
        statement = statement.where(Game.status == status)
    if genre is not None:
        statement = statement.where(Game.genre == genre)
    if linux_compat is not None:
        statement = statement.where(Game.linux_compat == linux_compat)

    statement = statement.order_by(Game.id).offset(skip).limit(limit)
    return list(db.scalars(statement).all())


def update_game(db: Session, game_id: int, game_in: GameUpdate) -> Game | None:
    game = get_game(db, game_id)
    if game is None:
        return None

    update_data = game_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is None and field not in CLEARABLE_FIELDS:
            continue
        setattr(game, field, value)

    db.commit()
    db.refresh(game)
    return game


def delete_game(db: Session, game_id: int) -> bool:
    game = get_game(db, game_id)
    if game is None:
        return False

    db.delete(game)
    db.commit()
    return True
