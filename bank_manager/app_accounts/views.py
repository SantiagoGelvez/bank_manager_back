from datetime import datetime, timedelta, UTC

import jwt
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view

from .models import CustomUser, AccountType, BankAccount, Transaction
from .serializers import UserSerializer, BankAccountSerializer, AccountTypeSerializer, TransactionSerializer
from .modules.common import get_user_from_jwt_token


# Authentication views

class SignUpView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        try:
            user = CustomUser.objects.get(username=username)
        except ObjectDoesNotExist:
            raise AuthenticationFailed('User not found')

        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect password')

        payload = {
            'uuid': str(user.uuid),
            'exp': datetime.now(UTC) + timedelta(minutes=30),
            'iat': datetime.now(UTC)
        }

        token = jwt.encode(payload, 'secret', algorithm='HS256')

        response = Response()
        response.set_cookie(key='jwt', value=token, httponly=True)

        user_seriliazer = UserSerializer(user)

        response.data = {
            'user': user_seriliazer.data,
            'jwt': token
        }
        return response


class UserView(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')
        user = get_user_from_jwt_token(token)
        serializer = UserSerializer(user)

        response = Response()
        response.data = {
            'user': serializer.data,
            'jwt': token
        }

        return response

    def put(self, request):
        token = request.COOKIES.get('jwt')
        user = get_user_from_jwt_token(token)
        serializer = UserSerializer(user, data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        response = Response()
        response.data = {
            'user': serializer.data,
            'jwt': token
        }

        return response


class LogoutView(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message': 'success'
        }
        return response


# Bank account views

@api_view(['GET'])
def get_account_types(request):
    """
    Get all account types
    :param request:
    :return: AccountTypeSerializer
    """
    account_type = AccountType.objects.all()
    return Response(AccountTypeSerializer(account_type, many=True).data)


@api_view(['POST'])
def register_bank_account(request):
    """
    Register a bank account
    :param request:
    :return: BankAccountSerializer
    """
    token = request.COOKIES.get('jwt')
    user = get_user_from_jwt_token(token)

    data = request.data.dict()
    data['user'] = user

    if int(data['balance']) < 0:
        return Response({'message': 'Invalid amount'}, status=status.HTTP_400_BAD_REQUEST)

    bank_account = BankAccount.create(**data)

    return Response(BankAccountSerializer(bank_account).data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def get_bank_account_list(request):
    """
    Get all bank accounts
    :param request:
    :return: List of BankAccountSerializer
    """
    token = request.COOKIES.get('jwt')
    user = get_user_from_jwt_token(token)
    bank_accounts = user.bankaccount_set.all()
    return Response(BankAccountSerializer(bank_accounts, many=True).data)


@api_view(['GET'])
def get_bank_account(request, uuid):
    """
    Get details of a bank account
    :param request:
    :param uuid:
    :return: BankAccountSerializer
    """
    token = request.COOKIES.get('jwt')
    user = get_user_from_jwt_token(token)

    bank_account = BankAccount.objects.get(uuid=uuid)

    if bank_account.user != user:
        return Response({'message': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

    return Response(BankAccountSerializer(bank_account).data)


@api_view(['POST'])
def deposit_to_account(request, uuid):
    """
    Deposit to a bank account
    :param request:
    :param uuid:
    :return: BankAccountSerializer
    """
    token = request.COOKIES.get('jwt')
    user = get_user_from_jwt_token(token)

    bank_account = BankAccount.objects.get(uuid=uuid)

    if bank_account.user != user:
        return Response({'message': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

    amount = request.data.get('amount')
    if int(amount) <= 0:
        return Response({'message': 'Invalid amount'}, status=status.HTTP_400_BAD_REQUEST)

    bank_account.deposit(amount)

    return Response(BankAccountSerializer(bank_account).data)


@api_view(['POST'])
def withdraw_from_account(request, uuid):
    """
    Withdraw from a bank account
    :param request:
    :param uuid:
    :return: BankAccountSerializer
    """
    token = request.COOKIES.get('jwt')
    user = get_user_from_jwt_token(token)

    bank_account = BankAccount.objects.get(uuid=uuid)

    if bank_account.user != user:
        return Response({'message': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

    amount = request.data.get('amount')
    if int(amount) <= 0:
        return Response({'message': 'Invalid amount'}, status=status.HTTP_400_BAD_REQUEST)

    if int(amount) > bank_account.total_balance:
        return Response({'message': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)

    bank_account.withdraw(amount)

    return Response(BankAccountSerializer(bank_account).data)


# Transaction views

class TransactionView(APIView):
    def get(self, request, uuid):
        """
        Get all transactions of a bank account
        :param request:
        :param uuid:
        :return: List of TransactionSerializer
        """
        token = request.COOKIES.get('jwt')
        user = get_user_from_jwt_token(token)

        bank_account = BankAccount.objects.get(uuid=uuid)

        if bank_account.user != user:
            return Response({'message': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        transactions = Transaction.objects.filter(bank_account=bank_account).order_by('-created_at')
        return Response(TransactionSerializer(transactions, many=True).data)
