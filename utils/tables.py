from datetime import datetime
from sqlalchemy import (
    Enum,
    ForeignKey as fk,
    PrimaryKeyConstraint as pkc,
)
from sqlalchemy.orm import (
    Mapped,
    declarative_base,
    mapped_column as column,
    relationship,
)
from .functions import (
    backref,
    childOf,
    defaultPrimaryKey as pk,
    positive,
)

Base = declarative_base()
GAME_MODES = ["versus", "ranked", "free", "coop", "unranked", "tourney"]


class User(Base):
    __tablename__: str = "users"

    id: Mapped[int] = pk()
    name: Mapped[str | None]
    elo: Mapped[int | None]

    # Relationships
    picks: Mapped[list["CO"]] = relationship(
        secondary="players",
        primaryjoin="User.id == Player.user_id",
        secondaryjoin="CO.id == Player.co_id",
        viewonly=True,
    )
    matches: Mapped["Match"] = relationship(
        secondary="players",
        primaryjoin="User.id == Player.user_id",
        secondaryjoin="Match.id == Player.match_id",
        viewonly=True,
    )


class CO(Base):
    __tablename__: str = "cos"

    id: Mapped[int] = pk()
    name: Mapped[str]

    picked_at: Mapped[list["Match"]] = relationship(
        secondary="players",
        primaryjoin="CO.id == Player.co_id",
        secondaryjoin="Match.id == Player.match_id",
        back_populates="co_picks",
        viewonly=True,
    )
    banned_at: Mapped[list["Match"]] = relationship(
        secondary="bans",
        primaryjoin="CO.id == Ban.co_id",
        secondaryjoin="Match.id == Ban.match_id",
        back_populates="bans",
        viewonly=True,
    )


class Map(Base):
    __tablename__: str = "maps"

    id: Mapped[int] = pk()
    name: Mapped[str]

    # Relationships
    matches: Mapped[list["Match"]] = backref("map")


class Ban(Base):
    __tablename__: str = "bans"

    match_id: Mapped[int] = column(fk("matches.id", ondelete="CASCADE"))
    co_id: Mapped[int] = column(fk("cos.id", ondelete="CASCADE"))

    __table_args__: tuple[pkc,] = (pkc("match_id", "co_id"),)


class Match(Base):
    __tablename__: str = "matches"

    id: Mapped[int] = pk()
    fow: Mapped[bool]
    mode: Mapped[str] = column(Enum(*GAME_MODES, name="mode_enum"))
    winner_id: Mapped[int] = positive("winner_id")
    ended: Mapped[datetime]
    map_id: Mapped[int] = column(fk("maps.id"))

    # Relationships
    players: Mapped[list["Player"]] = childOf("match")
    map: Mapped["Map"] = backref("matches")
    co_picks: Mapped[list["CO"]] = relationship(
        secondary="players",
        primaryjoin="Match.id == Player.match_id",
        secondaryjoin="CO.id == Player.co_id",
        back_populates="picked_at",
        viewonly=True,
    )
    bans: Mapped[list["CO"]] = relationship(
        secondary="bans",
        primaryjoin="Match.id == Ban.match_id",
        secondaryjoin="CO.id == Ban.co_id",
        back_populates="banned_at",
    )


class Player(Base):
    __tablename__: str = "players"

    id: Mapped[int] = positive("id")
    match_id: Mapped[int] = column(fk("matches.id"))

    user_id: Mapped[int] = column(fk("users.id"))
    co_id: Mapped[int] = column(fk("cos.id"))
    resulting_elo: Mapped[int] = positive("resulting_elo")

    # Relationships
    user: Mapped["User"] = relationship()
    pick: Mapped["CO"] = relationship()
    match: Mapped["Match"] = backref("players")

    __table_args__: tuple[pkc,] = (pkc("id", "match_id"),)
