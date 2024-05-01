from typing import List

import jwt
import tortoise.exceptions

from app.database.models.user import (User, User_Pydantic, UserIn_Pydantic, UserRole)
from app.helpers.constant import DB_URL
from app.helpers.mail import send_mail
from app.helpers.security import (create_verification_token,
                                  validate_token, SECRET_KEY, authenticate_user,
                                  get_current_user, has_permission)
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from passlib.hash import bcrypt

router = APIRouter()


@router.get("/health")
async def health_check():
    """
        A function to perform a health check, accessible only to admin users.
        Returns a dictionary containing the health status with the database URL.
    """
    return {'Health': DB_URL}


@router.post('/users')
async def create_user(user: UserIn_Pydantic):
    """
        Creates a new user based on the provided data in 'user' parameter.
        Hashes the user's password and saves the user to the database.
        Returns the created user object in a Pydantic model format.
    """

    try:

        if user.role.strip().lower() not in [member.name.lower() for member in UserRole]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user role"
            )
        user_obj = await User.create(**user.dict(exclude_unset=True))
        user_obj.password_hash = bcrypt.hash(user.password_hash)
        await user_obj.save()
        return await User_Pydantic.from_tortoise_orm(user_obj)
    except tortoise.exceptions.ValidationError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="One of the entry is not valid"
        )
    except tortoise.exceptions.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists"
        )



@router.get('/users', response_model=List[User_Pydantic])
async def get_users(user: UserIn_Pydantic = Depends(get_current_user)):
    """
        Retrieves and returns a list of all users from the database in a Pydantic model format.
        No parameters are required. Returns a list of User_Pydantic objects.
    """
    return await User_Pydantic.from_queryset(User.all())


@router.get('/users/me', response_model=User_Pydantic)
async def get_session_user(user: User_Pydantic = Depends(get_current_user)):
    """
        Retrieves the current user's information.
        Parameter:
            - user: User_Pydantic - the current user retrieved using 'get_current_user' function.
        Returns:
            - User_Pydantic: The Pydantic model object representing the current user.
    """
    return user


@router.get('/users/{user_id}', response_model=User_Pydantic)
async def get_user(user_id: int, user: UserIn_Pydantic = Depends(get_current_user)):
    """
        Retrieves a single user from the database based on the provided user_id.

        Parameters:
            - user_id: int - the unique identifier of the user to retrieve.
            - user: UserIn_Pydantic - the current user retrieved using 'get_current_user' function.

        Returns:
            - User_Pydantic: The Pydantic model object representing the requested user.
    """
    return await User_Pydantic.from_queryset_single(User.get(id=user_id))


@router.put('/users/{user_id}', response_model=User_Pydantic)
async def update_user(user_id: int, user: UserIn_Pydantic = Depends(get_current_user)):
    """
        Updates a user's information in the database.

        Parameters:
            - user_id: int - the unique identifier of the user to update.
            - user: UserIn_Pydantic - the user object containing the updated information.

        Returns:
            - User_Pydantic: The Pydantic model object representing the updated user.
    """
    user.password_hash = bcrypt.hash(user.password_hash)
    await User.get(id=user_id).update(**user.dict(exclude_unset=True))
    return await User_Pydantic.from_queryset_single(User.get(id=user_id))


@router.delete('/users/{user_id}')
async def delete_user(user_id: int, user: UserIn_Pydantic = Depends(get_current_user)):
    """
        Deletes a user from the database based on the provided user_id.

        Parameters:
            - user_id: int - the unique identifier of the user to delete.
            - user: UserIn_Pydantic - the current user retrieved using 'get_current_user' function.

        Returns:
            - dict: An empty dictionary.
    """
    await User.filter(id=user_id).delete()
    return {}


@router.post('/token')
async def generate_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
        Generates an access token for the user based on the provided OAuth2PasswordRequestForm data.

        Parameters:
            - form_data: OAuth2PasswordRequestForm - the form data containing the user's username and password.

        Returns:
            - dict: A dictionary containing the generated access token and token type.
    """
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid username or password'
        )
    user_obj = await User_Pydantic.from_tortoise_orm(user)
    token = jwt.encode(user_obj.dict(), SECRET_KEY)
    return {'access_token': token, 'token_type': 'bearer'}


@router.post('/forgot-password')
async def forgot_password(email: str):
    """
        Handles the forgot password functionality by sending a password reset token to the user's email.

        Parameters:
            - email (str): The email address of the user requesting a password reset.

        Returns:
            - None
    """
    user = await User.get(email=email)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    try:
        user_token_obj = await create_verification_token(user)
        send_mail(email, "VanUse - Reset Password", f'<strong>{user_token_obj.token}</strong>')
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Oops Something Went wrong {e.message}'
        )

    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(user_token_obj))


@router.post("/reset-password")
async def reset_password(reset_token: str, password: str, confirmed_password: str):
    """
        Handles the reset password functionality by validating the reset token, checking password match,
        updating the user's password hash, and returning the user details as a Pydantic model if successful.

        Parameters:
            - reset_token (str): The token used to reset the password.
            - password (str): The new password to set.
            - confirmed_password (str): The confirmation of the new password.

        Returns:
            - dict or JSONResponse: A dictionary with user details in Pydantic model format if successful,
              otherwise a JSONResponse with the result of the token validation.
    """
    result = await validate_token(reset_token)
    if result['status_code'] == 200 and password == confirmed_password:
        await User.get(id=result['user']).update(password_hash=bcrypt.hash(password))
        return await User_Pydantic.from_queryset_single(User.get(id=result['user']))
    return result
