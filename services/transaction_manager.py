from transactions.models import Transactions
from users.models import User



def record_transaction(user_id, amount, transaction_type , transaction_status = "completed"):
  try:
       
    user = User.objects.get(id=user_id)
    balance_before = user.balance
    balance_after = balance_before + amount
    
    Transactions.objects.create(user=user,
                                full_name=user.full_name if user.id != 2 else "منصة سراج التعليمية",
                                amount=amount,
                                transaction_type=transaction_type,
                                transaction_status=transaction_status,
                                balance_before=balance_before,
                                balance_after=balance_after)
  
    return True
  
  except Exception as e:
  
    return False