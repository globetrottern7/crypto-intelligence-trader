"""Add persistent paper account and trade ledger."""
from alembic import op
import sqlalchemy as sa

revision = "0003_paper_portfolio"
down_revision = "0002_market_candles"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "paper_accounts",
        sa.Column("id", sa.String(length=40), primary_key=True),
        sa.Column("initial_cash", sa.Numeric(20, 8), nullable=False),
        sa.Column("cash", sa.Numeric(20, 8), nullable=False),
        sa.Column("realised_pnl", sa.Numeric(20, 8), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "paper_trades",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("account_id", sa.String(length=40), sa.ForeignKey("paper_accounts.id"), nullable=False),
        sa.Column("symbol", sa.String(length=40), nullable=False),
        sa.Column("quantity", sa.Numeric(28, 12), nullable=False),
        sa.Column("entry_price", sa.Numeric(38, 18), nullable=False),
        sa.Column("entry_fee", sa.Numeric(20, 8), nullable=False),
        sa.Column("stop_loss", sa.Numeric(38, 18), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("opened_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("exit_price", sa.Numeric(38, 18), nullable=True),
        sa.Column("exit_fee", sa.Numeric(20, 8), nullable=True),
        sa.Column("realised_pnl", sa.Numeric(20, 8), nullable=True),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_paper_trades_account_id", "paper_trades", ["account_id"])
    op.create_index("ix_paper_trades_symbol", "paper_trades", ["symbol"])
    op.create_index("ix_paper_trades_status", "paper_trades", ["status"])


def downgrade() -> None:
    op.drop_index("ix_paper_trades_status", table_name="paper_trades")
    op.drop_index("ix_paper_trades_symbol", table_name="paper_trades")
    op.drop_index("ix_paper_trades_account_id", table_name="paper_trades")
    op.drop_table("paper_trades")
    op.drop_table("paper_accounts")
