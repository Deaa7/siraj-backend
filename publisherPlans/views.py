from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.shortcuts import get_object_or_404


from .serializers import PublisherPlanSerializer

# models
from .models import PublisherPlans
from users.models import User


@permission_classes([IsAuthenticated])
@api_view(["GET"])
def get_publisher_plan_statistics(request):

    user = request.user
    publisher_plan = PublisherPlans.objects.get(user=user)
    serializer = PublisherPlanSerializer(publisher_plan)
    return Response(serializer.data, status=status.HTTP_200_OK)

@permission_classes([IsAuthenticated])
@api_view(["PATCH"])
def update_auto_renew(request, plan_public_id):
    """
    Update the auto_renew field for a publisher plan.
    Only the plan owner can update their own plan.
    """
    try:
        user = request.user

        publisher_plan = get_object_or_404(PublisherPlans, public_id=plan_public_id)

        # Check if the user owns this plan
        if publisher_plan.user != user:
            return Response(
                {"error": "ليس لديك صلاحية لتعديل هذه الخطة"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Get the auto_renew value from request data
        auto_renew = request.data.get("auto_renew")

        if auto_renew is None:
            return Response(
                {"error": "يجب إرسال قيمة auto_renew"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate that auto_renew is a boolean
        if not isinstance(auto_renew, bool):

            return Response(
                {"error": "auto_renew يجب أن يكون true أو false"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Update only the auto_renew field
        publisher_plan.auto_renew = auto_renew
        publisher_plan.save()

        return Response(
            {"message": "تم تحديث إعدادات التجديد التلقائي بنجاح"},
            status=status.HTTP_200_OK,
        )
    except Exception as exc:
        return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
