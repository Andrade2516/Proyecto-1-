import pandas as pd
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.models import Game, LinuxCompat
from app.schemas import GenreStats, LinuxCompatStats, StatsSummary

router = APIRouter(prefix="/stats", tags=["stats"])


def games_dataframe(games: list[Game]) -> pd.DataFrame:
    records = [
        {
            "genre": game.genre,
            "hours_played": game.hours_played,
            "rating": game.rating,
            "linux_compat": game.linux_compat.value,
        }
        for game in games
    ]
    return pd.DataFrame(
        records,
        columns=["genre", "hours_played", "rating", "linux_compat"],
    )


@router.get("/summary", response_model=StatsSummary)
def get_summary(db: Session = Depends(get_db)) -> StatsSummary:
    df = games_dataframe(crud.get_all_games(db))
    total_games = len(df)

    total_hours = 0.0
    average_rating = None

    if total_games > 0:
        total_hours = round(float(df["hours_played"].sum()), 2)
        mean_rating = df["rating"].dropna().mean()
        if not pd.isna(mean_rating):
            average_rating = round(float(mean_rating), 2)

    return StatsSummary(
        total_games=total_games,
        total_hours=total_hours,
        average_rating=average_rating,
    )


@router.get("/by-genre", response_model=list[GenreStats])
def get_stats_by_genre(db: Session = Depends(get_db)) -> list[GenreStats]:
    df = games_dataframe(crud.get_all_games(db))
    if df.empty:
        return []

    df["genre"] = df["genre"].fillna("Unknown")
    grouped = (
        df.groupby("genre")
        .agg(
            total_games=("genre", "size"),
            total_hours=("hours_played", "sum"),
        )
        .reset_index()
        .sort_values(by=["total_games", "genre"], ascending=[False, True])
    )

    return [
        GenreStats(
            genre=row.genre,
            total_games=int(row.total_games),
            total_hours=round(float(row.total_hours), 2),
        )
        for row in grouped.itertuples(index=False)
    ]


@router.get("/linux-compat", response_model=list[LinuxCompatStats])
def get_stats_linux_compat(
    db: Session = Depends(get_db),
) -> list[LinuxCompatStats]:
    df = games_dataframe(crud.get_all_games(db))
    total_games = len(df)
    counts = df["linux_compat"].value_counts()

    stats = []
    for compat in LinuxCompat:
        count = int(counts.get(compat.value, 0))
        percentage = (
            round(count / total_games * 100, 2) if total_games > 0 else 0.0
        )
        stats.append(
            LinuxCompatStats(
                linux_compat=compat,
                total_games=count,
                percentage=percentage,
            )
        )

    return sorted(stats, key=lambda item: (-item.percentage, item.linux_compat.value))
