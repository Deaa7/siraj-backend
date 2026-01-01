from rest_framework import serializers
from django.utils import timezone

from .models import DiscountCodes   
from exams.models import Exam
from notes.models import Note
from courses.models import Course
from publisherOffers.models import PublisherOffers
from utils.validators import CommonValidators
from django.shortcuts import get_object_or_404



class DiscountCodeCreateSerializer(serializers.ModelSerializer):
    content_public_id = serializers.CharField(write_only=True, required=True)
    discount_code = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = DiscountCodes
        fields = [
            "publisher_id",
            "discount_for",
            "discount_code",
            "exam_id",
            "note_id",
            "course_id",
            "content_public_id",
            "discount_type",
            "discount_value",
            "discount_code",
            "valid_until",
            "number_of_remaining_uses",
        ]
        extra_kwargs = {
            "exam_id": {"required": False, "allow_null": True},
            "note_id": {"required": False, "allow_null": True},
            "course_id": {"required": False, "allow_null": True},
        }

    def validate_discount_code(self, value):

        if not value:
            raise serializers.ValidationError("كود الخصم مطلوب")

        if value and len(value) < 2:
            raise serializers.ValidationError("كود الخصم يجب أن يكون أطول من 2 حرف")
        
        return CommonValidators.validate_text_field(value, "كود الخصم")    
    
    def validate_discount_value(self, value):
        if value <= 0:
            raise serializers.ValidationError("قيمة الخصم يجب أن تكون أكبر من 0")
        return value

    def validate_valid_until(self, value):
        if value and value < timezone.now():
            raise serializers.ValidationError("تاريخ انتهاء الصلاحية يجب أن يكون في المستقبل")
        return value

    def validate(self, data):
        content_public_id = data.get("content_public_id")
        
        if not content_public_id:
            raise serializers.ValidationError({"content_public_id": "معرف المحتوى مطلوب"})
        
        # Validate discount value based on type
        discount_type = data.get("discount_type")
        discount_value = data.get("discount_value")
        
        if discount_type == "percentage" and discount_value > 100:
            raise serializers.ValidationError({"discount_value": "نسبة الخصم لا يمكن أن تكون أكثر من 100%"})
        
        return data

    def create(self, validated_data):
        validated_data.pop("content_public_id", None)
        return super().create(validated_data)


class DiscountCodeUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscountCodes
        fields = [
            "discount_type",
            "discount_value",
            "valid_until",
            "active",
            "number_of_remaining_uses",
        ]

    def validate_discount_value(self, value):
        if value and value <= 0:
            raise serializers.ValidationError("قيمة الخصم يجب أن تكون أكبر من 0")
        return value

    def validate_valid_until(self, value):
        if value and value < timezone.now():
            raise serializers.ValidationError("تاريخ انتهاء الصلاحية يجب أن يكون في المستقبل")
        return value

    def validate_number_of_remaining_uses(self, value):
        if value and value < 0:
            raise serializers.ValidationError("عدد الاستخدامات المتبقية يجب أن تكون أكبر من 0")
        return value
    
    def validate(self, data):
        discount_type = data.get("discount_type", self.instance.discount_type if self.instance else None)
        discount_value = data.get("discount_value", self.instance.discount_value if self.instance else None)
        
        if discount_type == "percentage" and discount_value and discount_value > 100:
            raise serializers.ValidationError({"discount_value": "نسبة الخصم لا يمكن أن تكون أكثر من 100%"})
        
        return data
    

class DiscountCodeDetailSerializer(serializers.ModelSerializer):
    publisher_name = serializers.SerializerMethodField("get_publisher_name")
    exam_public_id = serializers.CharField(source="exam_id.public_id", read_only=True, allow_null=True)
    note_public_id = serializers.CharField(source="note_id.public_id", read_only=True, allow_null=True)
    course_public_id = serializers.CharField(source="course_id.public_id", read_only=True, allow_null=True)
    offer_public_id = serializers.CharField(source="offer_id.public_id", read_only=True, allow_null=True)
    
    class Meta:
        model = DiscountCodes
        fields = [
            "public_id",
            "publisher_public_id",
            "publisher_name",
            "discount_for",
            "exam_public_id",
            "note_public_id",
            "course_public_id",
            "offer_public_id",
            "discount_type",
            "discount_value",
            "discount_code",
            "valid_until",
            "active",
            "number_of_uses",
            "number_of_remaining_uses",
            "created_at",
            "updated_at",
        ]
    
    def get_publisher_name(self, obj):
        name = ""
        if obj.publisher_id.account_type == "teacher":
            name = "الاستاذ " if obj.publisher_id.gender == "M" else "الآنسة " 
            name += obj.publisher_id.full_name
        elif obj.publisher_id.account_type == "team":
            name = "فريق " + obj.publisher_id.team_name
        return name


class DiscountCodeListSerializer(serializers.ModelSerializer):
    public_content_id = serializers.SerializerMethodField("get_public_content_id")
    content_name = serializers.SerializerMethodField("get_content_name")
    content_class = serializers.SerializerMethodField("get_content_class")
    content_subject_name = serializers.SerializerMethodField("get_content_subject_name")
    content_price = serializers.SerializerMethodField("get_content_price")
    class Meta:
        model = DiscountCodes
        fields = [
            "public_id",
            "discount_code",
            "discount_for",
            "public_content_id",
            "content_name",
            "content_class",
            "content_subject_name",
            "content_price",
            "discount_type",
            "discount_value",
            "valid_until",
            "active",
            "number_of_uses",
            "number_of_remaining_uses",
            "created_at",
        ]
    
    def get_public_content_id(self, obj):
        if obj.exam_id:
            return obj.exam_id.public_id
        elif obj.note_id:
            return obj.note_id.public_id
        elif obj.course_id:
            return obj.course_id.public_id
    
    def get_content_name(self, obj):
        if obj.exam_id:
            return obj.exam_id.name
        elif obj.note_id:
            return obj.note_id.name
        elif obj.course_id:
            return obj.course_id.name
    
    def get_content_class(self, obj):
        if obj.exam_id:
            return obj.exam_id.Class
        elif obj.note_id:
            return obj.note_id.Class
        elif obj.course_id:
            return obj.course_id.Class
    
    def get_content_subject_name(self, obj):
        if obj.exam_id:
         return obj.exam_id.subject_name
        elif obj.note_id:
            return obj.note_id.subject_name
        elif obj.course_id:
            return obj.course_id.subject_name
    
    def get_content_price(self, obj):
        if obj.exam_id:
            return obj.exam_id.price
        elif obj.note_id:
            return obj.note_id.price
        elif obj.course_id:
            return obj.course_id.price
 

class DiscountCodeValidateSerializer(serializers.ModelSerializer):
    new_price = serializers.SerializerMethodField(method_name="get_new_price" , required=False)
    content_public_id = serializers.CharField(write_only=True, required=True)
    discount_value = serializers.SerializerMethodField(method_name="get_discount_value" , required=False)
    class Meta:
        model = DiscountCodes
        fields = [
            "discount_code",
            "discount_for",
            "content_public_id",
            "new_price",
            "discount_value",
            
        ]
    
    def validate_discount_for(self, value):
        if not value:
            raise serializers.ValidationError("نوع المحتوى مطلوب")
        if value not in ["exam", "note", "course" , "offer"]:
            raise serializers.ValidationError("نوع المحتوى غير صحيح")
        return value
    
    def validate_content_public_id(self, value):
        if not value:
            raise serializers.ValidationError("معرف المحتوى مطلوب")
        return CommonValidators.validate_text_field(value, "معرف المحتوى")
    
    def validate_discount_code(self, value):
        if not value:
            raise serializers.ValidationError("كود الخصم")
        return CommonValidators.validate_text_field(value, "كود الخصم")
     
    def get_new_price(self, obj):
        content = None 
        discountObject =None
        if obj["discount_for"] == "exam":
            content = get_object_or_404(Exam, public_id=obj["content_public_id"])
            discountObject = DiscountCodes.objects.filter(  discount_code = obj["discount_code"] , exam_id = content , discount_for = obj["discount_for"] ,  active=True ).first()
 
        elif obj["discount_for"] == "note":
            content = get_object_or_404(Note, public_id=obj["content_public_id"])
            discountObject = DiscountCodes.objects.filter(  discount_code = obj["discount_code"] , note_id = content , discount_for = obj["discount_for"] ,  active=True ).first()
            
        elif obj["discount_for"] == "course":
            content = get_object_or_404(Course, public_id=obj["content_public_id"])
            discountObject = DiscountCodes.objects.filter(  discount_code = obj["discount_code"] , course_id = content , discount_for = obj["discount_for"] , active=True ).first()
        elif obj["discount_for"] == "offer":
            content = get_object_or_404(PublisherOffers, public_id=obj["content_public_id"])
            discountObject = DiscountCodes.objects.filter(  discount_code = obj["discount_code"] , offer_id = content , discount_for = obj["discount_for"]  , active=True ).first()
       
        if not content:
            raise serializers.ValidationError("المحتوى غير موجود")
        
        if not discountObject:
            raise serializers.ValidationError("كود الخصم غير صحيح أو غير نشط")
  
        if discountObject.number_of_remaining_uses is not None and discountObject.number_of_uses >= discountObject.number_of_remaining_uses:
            raise serializers.ValidationError("لا يوجد استخدامات متبقية لهذا الكود")
        
        if discountObject.valid_until is not None and discountObject.valid_until < timezone.now():
            raise serializers.ValidationError("تاريخ انتهاء الصلاحية لهذا الكود قد انتهى")
        
        
        if discountObject.discount_type == "percentage":
            if obj["discount_for"] == "offer":
                return round(content.offer_price * (1 - discountObject.discount_value / 100), 2)
            else:
             return round(content.price * (1 - discountObject.discount_value / 100), 2)
        else:
            if obj["discount_for"] == "offer":
                return round(content.offer_price - discountObject.discount_value, 2)
            else:
                return round(content.price - discountObject.discount_value, 2)
        
  
   
    def get_discount_value(self, obj):
        content = None 
        discountObject =None
        if obj["discount_for"] == "exam":
            content = get_object_or_404(Exam, public_id=obj["content_public_id"])
            discountObject = DiscountCodes.objects.filter(  discount_code = obj["discount_code"] , exam_id = content , discount_for = obj["discount_for"] ,  active=True ).first()
 
        elif obj["discount_for"] == "note":
            content = get_object_or_404(Note, public_id=obj["content_public_id"])
            discountObject = DiscountCodes.objects.filter(  discount_code = obj["discount_code"] , note_id = content , discount_for = obj["discount_for"] ,  active=True ).first()
            
        elif obj["discount_for"] == "course":
            content = get_object_or_404(Course, public_id=obj["content_public_id"])
            discountObject = DiscountCodes.objects.filter(  discount_code = obj["discount_code"] , course_id = content , discount_for = obj["discount_for"] , active=True ).first()
        elif obj["discount_for"] == "offer":
            content = get_object_or_404(PublisherOffers, public_id=obj["content_public_id"])
            discountObject = DiscountCodes.objects.filter(  discount_code = obj["discount_code"] , offer_id = content , discount_for = obj["discount_for"]  , active=True ).first()
       
        if not content:
            raise serializers.ValidationError("المحتوى غير موجود")
        
        if not discountObject:
            raise serializers.ValidationError("كود الخصم غير صحيح أو غير نشط")
  
 
        discount_value = ""
        if discountObject.discount_type == "percentage":
            discount_value = str(discountObject.discount_value) + "%"
        else :
            discount_value = str(discountObject.discount_value) + "ل.س"
        
        return discount_value
    
       
    