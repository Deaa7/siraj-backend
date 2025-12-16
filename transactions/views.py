from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from rest_framework.response import Response
from rest_framework import status
from .models import Transactions
from .serializers import TransactionsSerializer
from rest_framework.decorators import api_view
from services.parameters_validator import validate_pagination_parameters

@permission_classes([IsAuthenticated])
@api_view(['GET'])
def get_transactions_history_preview_of_publisher(request):
    
    """
     get only newest 5 transactions for the publisher
    """
    
    transactions = Transactions.objects.filter(user=request.user).order_by('-created_at')

    end = 5
    if len(transactions) < end:
        end = len(transactions)
    serializer = TransactionsSerializer(transactions[:end], many=True)
    
    
    
    return Response({"history": serializer.data}, status=status.HTTP_200_OK)
    
    

@permission_classes([IsAuthenticated])
@api_view(['GET'])
def get_transactions_history_of_publisher(request):
    
    """
     get transactions history for the publisher with pagination
    """
    
    count,limit = validate_pagination_parameters(
        int(request.query_params.get('count', 0)), 
        int(request.query_params.get('limit', 10))
    )
    
    transactions = Transactions.objects.filter(user=request.user).order_by('-created_at')
  
    total = transactions.count()
    begin = count * limit
    end = (count + 1) * limit
    
    if total < end:
        end = total
        
    if begin > total:
        begin = total
    
    serializer = TransactionsSerializer(transactions[begin:end], many=True)
    
    return Response({"history": serializer.data , "total_number": total}, status=status.HTTP_200_OK)
    
    