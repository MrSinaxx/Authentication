from fastapi.routing import APIRouter
from fastapi import Depends, HTTPException, status
from app.schema.schemas import UserRequest, UserRequestLogin
from app.schema.schemas import UserResponse, UserProfileRequest, UserProfileResponse
from app.services.services import UserService, get_user_service
from app.core.config import CREATE_OTP_ENDPOINT, VERIFY_OTP_ENDPOINT
from fastapi.responses import FileResponse

router = APIRouter(tags=["account"])


@router.post(
    "/signup",
    summary="Create new user",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponse,
)
async def create_user(
    data: UserRequest, user_service: UserService = Depends(get_user_service)
):
    """
    Endpoint to create a new user.

    Args:
        data (UserRequest): User information.
        user_service (UserService, optional): User service dependency. Defaults to Depends(get_user_service).

    Returns:
        UserResponse: Created user data.
    """
    try:
        user_data = await user_service.create_user(data)
        return user_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}",
        )


@router.post(
    "/verify_account",
    summary="Verify user",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=UserResponse,
)
async def login(
    data: UserRequestLogin, user_service: UserService = Depends(get_user_service)
):
    """
    Endpoint to verify a user.

    Args:
        data (UserRequestLogin): User login information.
        user_service (UserService, optional): User service dependency. Defaults to Depends(get_user_service).

    Returns:
        UserResponse: Verified user data.
    """
    try:
        user = await user_service.authenticate(
            data.username, data.password, data.totp_code
        )
        user["id"] = str(user["_id"])
        return user
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error verifying user: {str(e)}",
        )


@router.post(
    "/user_profile",
    summary="Get user profile",
    response_model=UserProfileResponse,
)
async def get_user_profile(
    profile_request: UserProfileRequest,
    user_service: UserService = Depends(get_user_service),
):
    """
    Endpoint to get user profile.

    Args:
        profile_request (UserProfileRequest): Request containing user_id.
        user_service (UserService, optional): User service dependency. Defaults to Depends(get_user_service).

    Returns:
        UserProfileResponse: User profile data.
    """
    try:
        user_id = profile_request.user_id
        user_profile = await user_service.get_user_profile(user_id)
        if user_profile is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found",
            )
        return user_profile
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting user profile: {str(e)}",
        )
