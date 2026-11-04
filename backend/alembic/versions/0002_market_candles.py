"""Add venue-aware OHLCV market candle storage."""
from alembic import op
import sqlalchemy as sa

revision = "0002_market_candles"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "market_candles",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("venue", sa.String(length=40), nullable=False),
        sa.Column("symbol", sa.String(length=40), nullable=False),
        sa.Column("interval", sa.String(length=8), nullable=False),
        sa.Column("open_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("close_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("open", sa.Numeric(38, 18), nullable=False),
        sa.Column("high", sa.Numeric(38, 18), nullable=False),
        sa.Column("low", sa.Numeric(38, 18), nullable=False),
        sa.Column("close", sa.Numeric(38, 18), nullable=False),
        sa.Column("volume", sa.Numeric(38, 18), nullable=False),
        sa.Column("is_closed", sa.Boolean(), nullable=False),
        sa.Column("ingested_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("venue", "symbol", "interval", "open_time",
                            name="uq_market_candle_identity"),
    )
    op.create_index("ix_market_candles_venue", "market_candles", ["venue"])
    op.create_index("ix_market_candles_symbol", "market_candles", ["symbol"])


def downgrade() -> None:
    op.drop_index("ix_market_candles_symbol", table_name="market_candles")
    op.drop_index("ix_market_candles_venue", table_name="market_candles")
    op.drop_table("market_candles")
