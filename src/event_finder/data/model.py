from pydantic import BaseModel


class ChatRecord(BaseModel):
    user: str 
    message: str
    ts: float
    seqid: int
