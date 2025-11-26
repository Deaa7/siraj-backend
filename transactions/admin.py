from django.contrib import admin
from .models import Transactions
# Register your models here.

@admin.register(Transactions)
class TransactionsAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "full_name",
        "amount",
        "transaction_type",
        "transaction_status",
        "balance_before",
        "balance_after",
        "created_at",
    ]
