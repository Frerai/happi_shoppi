# For customizing serializers, fields, in creation of new users.
from djoser.serializers import UserSerializer as BaseUserSerializer, UserCreateSerializer as BaseUserCreateSerializer


class UserCreateSerializer(BaseUserCreateSerializer):
    # This custom Meta class inherits everything from the Meta class og BaseUserCreateSerializer. Additionally, custom fields are added.
    class Meta(BaseUserCreateSerializer.Meta):
        # Overwritten, and additionally added fields.
        fields = ["id", "username", "password",
                  "email", "first_name", "last_name"]


class UserSerializer(BaseUserSerializer):
    # Custom fields, fname lname, to be returned when user is authenticated via JWT (at /auth/users/me/).
    class Meta(BaseUserSerializer.Meta):
        fields = ["id", "username", "email", "first_name", "last_name"]
