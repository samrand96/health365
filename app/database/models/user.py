import enum
from tortoise import fields
from tortoise.models import Model
from tortoise.contrib.pydantic import pydantic_model_creator
from passlib.hash import bcrypt


class UserRole(str, enum.Enum):

    SECRETARY = 'secretary'
    DOCTOR = 'doctor'
    LABORATORY = 'laboratory'


class User(Model):
    id = fields.IntField(pk=True)
    email = fields.CharField(max_length=50, unique=True)
    password_hash = fields.CharField(max_length=128, null=False)
    role = fields.CharEnumField(UserRole, null=False)

    def verify_password(self, password):
        return bcrypt.verify(password, self.password_hash)


User_Pydantic = pydantic_model_creator(User, name='User')
UserIn_Pydantic = pydantic_model_creator(User, name='UserIn', exclude_readonly=True)


class UserToken(Model):
    token = fields.UUIDField(max_length=36, pk=True)
    user = fields.ForeignKeyField('models.User', related_name='user')
    created_at = fields.DatetimeField(null=True, auto_now_add=True, use_tz=False)


UserToken_Pydantic = pydantic_model_creator(UserToken, name='UserToken')
UserTokenIn_Pydantic = pydantic_model_creator(UserToken, name='UserTokenIn', exclude_readonly=True)
