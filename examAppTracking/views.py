from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes, api_view
from rest_framework.response import Response
from rest_framework import status

from studentSubjectTracking.models import StudentSubjectTracking
from utils.validators import CommonValidators
from .serializers import ExamAppTrackingCardsSerializer
from .models import ExamAppTracking
from exams.models import Exam
from django.shortcuts import get_object_or_404
from datetime import datetime
from services.parameters_validator import validate_pagination_parameters


@permission_classes([IsAuthenticated])
@api_view(["POST"])
def create_exam_app_tracking(request, exam_public_id):

    try:

        user = request.user  # student info
        exam = get_object_or_404(Exam, public_id=exam_public_id)

        if user is None:
            return Response(
                {"error": "مستخدم غير موجود"}, status=status.HTTP_404_NOT_FOUND
            )

        exam_app_tracking, created = ExamAppTracking.objects.get_or_create(
            exam_id=exam,
            publisher_id=exam.publisher_id,
            student_id=user,
            number_of_apps=1,
        )

        if created:
            subject_tracking = StudentSubjectTracking.objects.get(
                student_id=user,
                subject_name=exam.subject_name,
            )
            subject_tracking.number_of_apps += 1
            subject_tracking.save()

        exam.number_of_apps += 1
        exam.save()

        return Response(status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@api_view(["GET"])
def get_exam_app_tracking_cards(request, public_student_id):

    try:
        limit, count = validate_pagination_parameters(
            request.data.get("count", 0), request.data.get("limit", 7)
        )

        begin = count * limit
        end = (count + 1) * limit
        exam_app_trackings = ExamAppTracking.objects.select_related(
            "exam_id", "student_id"
        ).filter(student_id__uuid=public_student_id)

        if begin > exam_app_trackings.count():
            begin = exam_app_trackings.count()

        if end > exam_app_trackings.count():
            end = exam_app_trackings.count()

        serializer = ExamAppTrackingCardsSerializer(
            exam_app_trackings[begin:end], many=True
        )

        return Response(
            {
                "exam_tracking_cards": serializer.data,
                "total_number": exam_app_trackings.count(),
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@api_view(["PATCH"])
def update_exam_app_tracking_metrics(request, exam_public_id):

    try:
        result = request.data.get("result")
        time = request.data.get("time")

        result = CommonValidators.validate_float_field(result, "result")
        time = CommonValidators.validate_integer_field(time, "time")

        user = request.user  # student info
        exam = get_object_or_404(Exam, public_id=exam_public_id)

        if user is None:
            return Response(
                {"error": "مستخدم غير موجود"}, status=status.HTTP_404_NOT_FOUND
            )

        exam_app_tracking = get_object_or_404(
            ExamAppTracking, exam_id=exam, student_id=user
        )
        # Update tracking metrics here

        exam_app_tracking.number_of_apps += 1

        if exam_app_tracking.result_of_first_app == 1000:  # initial value
            exam_app_tracking.result_of_first_app = result

        exam_app_tracking.result_of_last_app = result
        exam_app_tracking.last_app_date = datetime.now()
        exam_app_tracking.highest_score = max(exam_app_tracking.highest_score, result)
        exam_app_tracking.lowest_score = min(exam_app_tracking.lowest_score, result)
        exam_app_tracking.result_average = round(
            (exam_app_tracking.result_average + result) / 2, 2
        )

        if exam_app_tracking.time_of_first_app == 0:  # initial value
            exam_app_tracking.time_of_first_app = time

        if exam_app_tracking.shortest_time == 0:  # initial value
            exam_app_tracking.shortest_time = time

        else:
            exam_app_tracking.shortest_time = min(exam_app_tracking.shortest_time, time)

        exam_app_tracking.save()

        return Response(status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
