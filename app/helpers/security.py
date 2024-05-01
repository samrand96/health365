import copy, uuid, jwt
from datetime import datetime
from app.database.models.user import User, User_Pydantic, UserToken, UserRole
from fastapi import Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from tortoise import timezone
from app.helpers.constant import SECRET_KEY, ALGORITHM


async def validate_token(reset_token):
    """
        Validate a token by checking if it exists in the database and if it has expired.

        Parameters:
        reset_token (str): The token to be validated.

        Returns:
        dict: A dictionary with the status code and the user ID if the token is valid.
        JSONResponse: A JSON response with a 404 status code and a message if the token is expired or invalid.
    """
    user_token = await UserToken.get(token=reset_token)
    if user_token is not None:
        user_id = copy.deepcopy(user_token.user_id)
        diff = datetime.now() - timezone.make_naive(user_token.created_at, timezone=None)
        if diff.total_seconds() < 300:
            await UserToken.filter(token=reset_token).delete()
            return {'status_code': 200, 'user': user_id}
        await UserToken.filter(token=reset_token).delete()
        return JSONResponse(status_code=404, content="Token Expired")
    return JSONResponse(status_code=404, content="Invalid Token")


async def create_verification_token(user):
    """
        A function to create a verification token for a user.

        Parameters:
            user: The user object for whom the verification token is being created.

        Returns:
            The created user token object.
    """
    user_token_obj = await UserToken(token=uuid.uuid4())
    user_token_obj.created_at = datetime.now()
    user_token_obj.user = user
    await user_token_obj.save()
    return await user_token_obj


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def authenticate_user(username: str, password: str):
    """
        Authenticates a user based on the provided username and password.

        Parameters:
            - username (str): The username of the user to authenticate.
            - password (str): The password of the user to authenticate.

        Returns:
            - User: The authenticated user object if successful, False otherwise.
    """
    user = await User.get(email=username)
    if not user:
        return False
    if not user.verify_password(password):
        return False
    return user


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
        Retrieves the current user based on the provided token.

        Parameters:
            - token (str): The authentication token to decode and retrieve the user information.

        Returns:
            - User_Pydantic: The Pydantic model object representing the current user.

        Raises:
            - HTTPException: If the token is invalid or the user information cannot be retrieved, raises HTTP 401 Unauthorized.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user = await User.get(id=payload.get('id'))
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid username or password'
        )

    return await User_Pydantic.from_tortoise_orm(user)


def verify_token(token: str):
    """
        Function to verify the authenticity of a token by decoding it using the provided SECRET_KEY and ALGORITHM.

        Parameters:
            token (str): The token to be verified.

        Returns:
            dict: The payload extracted from the decoded token if verification is successful.

        Raises:
            HTTPException: If there is an error decoding the token, it raises an HTTPException with status code 403.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.DecodeError as e:
        raise HTTPException(status_code=403, detail=str(e))


def has_permission(required_roles: list[UserRole]):
    """
    A function that checks if a user has the required permissions based on their role.

    Parameters:
        required_roles (list): A list of roles that are required to access the resource.

    Returns:
        dict: A dictionary containing user information like id, role, is_doctor status, and token payload.
    """

    def role_checker(token: str = Depends(oauth2_scheme)):
        """
            A function that checks the user's role based on the provided token and verifies if the user has the required roles to access a resource.

            Parameters:
                token (str): The token used for authentication. Defaults to an OAuth2Scheme.

            Returns:
                dict: A dictionary containing user information including id, role, is_doctor status, and token payload.
        """
        payload = verify_token(token)
        user_role = payload.get('role')
        user_id: int = payload.get("id")
        user_role_str: str = payload.get("role")
        # user_role_str.strip().lower() not in [member.name.lower() for member in UserRole]
        # check which UserRole is equal to user_role_str then assign it to user_role

        try:
            for role in UserRole:
                if role.name.lower() == user_role_str.lower():
                    user_role = role
        except KeyError:
            raise HTTPException(status_code=403, detail="Invalid user role")

        is_doctor: bool = user_role == UserRole.DOCTOR

        if user_role not in required_roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return {"id": user_id, "role": user_role, "is_doctor": is_doctor, "token_payload": payload}

    return role_checker


def authenticated():
    def is_authenticated(token: str = Depends(oauth2_scheme)):
        payload = verify_token(token)
        user_id: int = payload.get("id")

        return {"token_payload": payload}

    return is_authenticated
