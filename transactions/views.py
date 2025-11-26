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
    
    transactions = Transactions.objects.filter(user=request.user)

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
    
    limit, count = validate_pagination_parameters(request.data.get('limit', 5), request.data.get('count', 0))
    
    transactions = Transactions.objects.filter(user=request.user)
  
    begin = count * limit
    end = (count + 1) * limit
    
    if len(serializer.data) < end:
        end = len(serializer.data)
        
    if begin > len(serializer.data):
        begin = len(serializer.data)
    
    serializer = TransactionsSerializer(transactions[begin:end], many=True)
    
    return Response({"history": serializer.data , "total_number": len(serializer.data)}, status=status.HTTP_200_OK)
    
    