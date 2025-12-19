from pydantic import BaseModel


class SRoleGet(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

