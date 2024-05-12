import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    uuid = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, verbose_name='UUID')
    phone = models.CharField(max_length=15, null=True, blank=True, verbose_name='Phone Number')


class AbstractStatus(models.Model):
    code = models.CharField(max_length=3, primary_key=True, unique=True)
    name = models.CharField(max_length=20)

    class Meta:
        abstract = True


class AbstractType(models.Model):
    code = models.CharField(max_length=3, primary_key=True, unique=True)
    name = models.CharField(max_length=20)
    description = models.TextField()

    class Meta:
        abstract = True


class AccountStatus(AbstractStatus):
    def __str__(self):
        return f'{self.code} - {self.name}'


class TransactionStatus(AbstractStatus):
    def __str__(self):
        return f'{self.code} - {self.name}'


class AccountType(AbstractType):
    def __str__(self):
        return f'{self.code} - {self.name}'


class TransactionType(AbstractType):
    def __str__(self):
        return f'{self.code} - {self.name}'


class BankAccount(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=20)
    account_name = models.CharField(max_length=100, null=True)
    account_type = models.ForeignKey(AccountType, to_field="code", on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.account_number} - {self.account_name}'

    @property
    def actual_status(self):
        return BankAccountStatusLog.objects.filter(bank_account=self).order_by('created_at').last().status

    @property
    def total_balance(self):
        income = Transaction.objects.filter(bank_account=self, transaction_type__code__in=['DEP', 'IDP']).aggregate(
            total=models.Sum('amount'))['total'] or 0
        expense = Transaction.objects.filter(bank_account=self, transaction_type__code='WTH').aggregate(
            total=models.Sum('amount'))['total'] or 0
        return income - expense

    @staticmethod
    def create(**kwargs):
        balance = kwargs.pop('balance', 0)

        account_type = kwargs.pop('account_type')
        kwargs['account_type'] = AccountType.objects.get(code=account_type)

        account = BankAccount(**kwargs)
        account.save()

        BankAccountStatusLog.objects.create(bank_account=account, status=AccountStatus.objects.get(code='A'),
                                            notes='Account created')
        Transaction.objects.create(bank_account=account, transaction_type=TransactionType.objects.get(code='IDP'),
                                   transaction_status=TransactionStatus.objects.get(code='S'), amount=balance)
        return account

    def deposit(self, amount):
        Transaction.objects.create(bank_account=self, transaction_type=TransactionType.objects.get(code='DEP'),
                                   transaction_status=TransactionStatus.objects.get(code='S'), amount=amount)

    def withdraw(self, amount):
        Transaction.objects.create(bank_account=self, transaction_type=TransactionType.objects.get(code='WTH'),
                                   transaction_status=TransactionStatus.objects.get(code='S'), amount=amount)


class BankAccountStatusLog(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bank_account = models.ForeignKey(BankAccount, on_delete=models.CASCADE)
    status = models.ForeignKey(AccountStatus, to_field="code", on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(null=True)

    def __str__(self):
        return f'{self.bank_account} - {self.status}'


class Transaction(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bank_account = models.ForeignKey(BankAccount, on_delete=models.CASCADE)
    transaction_type = models.ForeignKey(TransactionType, to_field="code", on_delete=models.SET_NULL, null=True)
    transaction_status = models.ForeignKey(TransactionStatus, to_field="code", on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.transaction_type} - {self.amount}'
