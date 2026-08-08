"""JSON auth API: token issue and current user."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.deps import require_user
from app.auth.passwords import verify_password
from app.auth.tokens import create_token
from app.auth.users import get_user_by_username
from app.models.auth import TokenRequest, TokenResponse, UserPublic

router = APIRouter()


@router.post(
    "/token",
    response_model=TokenResponse,
    summary="Issue an API Bearer token",
)
async def issue_token(body: TokenRequest) -> TokenResponse:
    user = await get_user_by_username(body.username.strip())
    if user is None or not verify_password(body.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    raw = await create_token(user["id"])
    return TokenResponse(access_token=raw)


@router.get(
    "/me",
    response_model=UserPublic,
    summary="Current user (session or Bearer)",
)
async def me(user: dict = Depends(require_user)) -> UserPublic:
    return UserPublic(id=user["id"], username=user["username"])
