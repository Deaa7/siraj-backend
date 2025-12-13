from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes, api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Unit
from users.models import User
from .serializers import (
    UnitListSerializer,
    UnitCRUDSerializer,
    UnitDetailSerializer,
)
from Constants import CLASSES_ARRAY, SUBJECT_NAMES_ARRAY


@permission_classes([IsAuthenticated])
@api_view(["GET"])
def get_units(request):
    """
    Get list of units - only returns name and slug
    Can be filtered by Class and subject_name
    No pagination
    """
    try:
        Class = request.query_params.get("Class" , "")
        subject_name = request.query_params.get("subject_name" , "")


        # Filter by Class if provided
        if Class:
            if Class not in CLASSES_ARRAY:
                return Response(
                    {"error": "الصف غير متوفر"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Filter by subject_name if provided
        if subject_name:
            if subject_name not in SUBJECT_NAMES_ARRAY:
                return Response(
                    {"error": "المادة غير متوفرة"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
                
            units = Unit.objects.filter(Class=Class, subject_name=subject_name)

        serializer = UnitListSerializer(units, many=True)
        return Response(
            {"units": serializer.data},
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@api_view(["GET"])
def get_unit_detail(request, unit_public_id):
    """
    Get unit details by public_id
    """
    try:
        unit = get_object_or_404(Unit, public_id=unit_public_id)
        serializer = UnitDetailSerializer(unit)
        return Response(
            {"unit": serializer.data},
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@api_view(["POST"])
def create_unit(request):
    """
    Create a new unit
    """
    try:
        user = request.user
        user = get_object_or_404(User, id = user.id)
        if user.account_type != "teacher":
            return Response(
                {"error": "ليس لديك صلاحية لإنشاء الوحدة"},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = UnitCRUDSerializer(data=request.data)

        if serializer.is_valid():
            unit = serializer.save()
            return Response(
                { "message": "تم إنشاء الوحدة بنجاح"},
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@api_view(["PUT", "PATCH"])
def update_unit(request, unit_public_id):
    
    """
    Update an existing unit
    """
    try:
        user = request.user
        user = get_object_or_404(User, id = user.id)
        if user.account_type != "admin":
            return Response(
                {"error": "ليس لديك صلاحية لتحديث الوحدة"},
                status=status.HTTP_403_FORBIDDEN,
            )
        unit = get_object_or_404(Unit, public_id=unit_public_id)

        # Use partial=True for PATCH, False for PUT
        partial = request.method == "PATCH"
        serializer = UnitCRUDSerializer(unit, data=request.data, partial=partial)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save()
        detail_serializer = UnitDetailSerializer(unit)

        return Response(
            {"unit": detail_serializer.data},
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@api_view(["DELETE"])
def delete_unit(request, unit_public_id):
    """
    Delete a unit
    """
    try:
        user = request.user
        user = get_object_or_404(User, id = user.id)
        if user.account_type != "admin":
            return Response(
                {"error": "ليس لديك صلاحية لحذف الوحدة"},
                status=status.HTTP_403_FORBIDDEN,
            )
        unit = get_object_or_404(Unit, public_id=unit_public_id)
        unit.delete()
        return Response(
            {"message": "تم حذف الوحدة بنجاح"},
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
