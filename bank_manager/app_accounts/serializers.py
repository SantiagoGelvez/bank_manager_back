from rest_framework import serializers
from .models import CustomUser, BankAccount, AccountType, BankAccountStatusLog, AccountStatus, TransactionType, \
    Transaction, TransactionStatus


class UserSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(format='hex_verbose', read_only=True, required=False)

    class Meta:
        model = CustomUser
        fields = ['uuid', 'username', 'first_name', 'last_name', 'email', 'password', 'phone']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


class AccountTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountType
        fields = ['code', 'name', 'description']


class AccountStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountStatus
        fields = ['code', 'name']


class BankAccountSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(format='hex_verbose', read_only=True, required=False)
    actual_status = AccountStatusSerializer(read_only=True)
    account_type = AccountTypeSerializer(read_only=True)
    total_balance = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = BankAccount
        fields = ['uuid', 'account_number', 'account_name', 'account_type', 'actual_status', 'total_balance']


class BankAccountStatusLogSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(format='hex_verbose', read_only=True, required=False)

    class Meta:
        model = BankAccountStatusLog
        fields = ['uuid', 'bank_account', 'status', 'created_at', 'notes']


class TransactionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionType
        fields = ['code', 'name', 'description']


class TransactionStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionStatus
        fields = ['code', 'name']


class TransactionSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(format='hex_verbose', read_only=True, required=False)
    bank_account = BankAccountSerializer(read_only=True)
    transaction_type = TransactionTypeSerializer(read_only=True)
    transaction_status = TransactionStatusSerializer(read_only=True)

    class Meta:
        model = Transaction
        fields = ['uuid', 'bank_account', 'transaction_type', 'transaction_status', 'amount', 'created_at']
