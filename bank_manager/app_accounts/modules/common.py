import jwt
from rest_framework.exceptions import AuthenticationFailed
from ..models import CustomUser


def get_user_from_jwt_token(token):
    if not token:
        raise AuthenticationFailed('Unauthenticated')

    try:
        payload = jwt.decode(token, 'secret', algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('Unauthenticated')

    user = CustomUser.objects.get(uuid=payload['uuid'])
    return user
