from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.models import Game
from app.schemas import GameCreate, GameRead, GameUpdate

router = APIRouter(prefix="/games", tags=["games"])


@router.post("", response_model=GameRead, status_code=status.HTTP_201_CREATED)
def create_game(game_in: GameCreate, db: Session = Depends(get_db)) -> Game:
    return crud.create_game(db, game_in)


@router.get("", response_model=list[GameRead])
def list_games(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[Game]:
    return crud.get_games(db, skip=skip, limit=limit)


@router.get("/{game_id}", response_model=GameRead)
def get_game(game_id: int, db: Session = Depends(get_db)) -> Game:
    game = crud.get_game(db, game_id)
    if game is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found",
        )
    return game


@router.put("/{game_id}", response_model=GameRead)
def update_game(
    game_id: int,
    game_in: GameUpdate,
    db: Session = Depends(get_db),
) -> Game:
    game = crud.update_game(db, game_id, game_in)
    if game is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found",
        )
    return game


@router.delete("/{game_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_game(game_id: int, db: Session = Depends(get_db)) -> Response:
    if not crud.delete_game(db, game_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
