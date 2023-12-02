from django.contrib.auth import get_user_model
from ninja import ModelSchema

from brewers.models import Brewer


User = get_user_model()


class UserSchema(ModelSchema):
    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
        ]
    # username: str
    # # Unauthenticated users don't have the following fields, so provide defaults.
    # email: str = None
    # first_name: str = None
    # last_name: str = None


class UserLimitedSchema(ModelSchema):
    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
        ]


class UserRegisterSchema(ModelSchema):
    class Meta:
        model = User
        fields = [
            "username",
            "password",
            "email",
            "first_name",
            "last_name",
        ]


class CreateBrewerSchema(ModelSchema):
    location_str: str
    class Meta:
        model = Brewer
        fields = [
            "phone_number",
        ]


class BrewerResponseSchema(ModelSchema):
    user: UserSchema
    location_str: str
    class Meta:
        model = Brewer
        fields = [
            "user",
            "phone_number",
            "can_claim",
        ]

    @staticmethod
    def resolve_phone_number(obj, context):
        return str(obj.phone_number)
