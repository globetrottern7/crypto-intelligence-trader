from pydantic import BaseModel, Field


class PaperOpenRequest(BaseModel):
    symbol: str = Field(min_length=3, max_length=40)
    quantity: float = Field(gt=0)
    stop_loss: float = Field(gt=0)


class PaperCloseRequest(BaseModel):
    trade_id: int = Field(gt=0)
