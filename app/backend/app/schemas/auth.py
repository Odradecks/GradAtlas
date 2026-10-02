from pydantic import BaseModel, Field


class AuthIn(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=8, max_length=128)


class UserOut(BaseModel):
    id: int
    email: str
    name: str | None
    google: bool


class MeOut(BaseModel):
    user: UserOut | None


class FavoritesIn(BaseModel):
    keys: list[str] = Field(max_length=200)


class FavoritesOut(BaseModel):
    keys: list[str]


class ProvidersOut(BaseModel):
    google: bool
