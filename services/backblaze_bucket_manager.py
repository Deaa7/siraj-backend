 
 
 


from django.conf import settings
import boto3
from django.utils import timezone
from tempUploads.models import TempUpload


def delete_temp_uploads_from_bucket():
    
    
    
    
    
        temp_files = TempUpload.objects.filter(expiration_date__lt=timezone.now())
       
        if not temp_files.exists():
           return True
       
        objects_to_delete = [{'Key': file.name} for file in temp_files]
        client = boto3.client(
        's3',
        endpoint_url=settings.AWS_PRIVATE_ENDPOINT_URL,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )

        try:
 
            client.delete_objects(
                Bucket=settings.AWS_PRIVATE_BUCKET_NAME,
                Delete={
                    'Objects': objects_to_delete,
                    'Quiet': True
                }
            )

            temp_files.delete()

            return True

        except Exception as e:
          return False
      
      
def delete_video_from_bucket(name : str):
         
        client = boto3.client(
        's3',
        endpoint_url=settings.AWS_PRIVATE_ENDPOINT_URL,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )

        try:
 
            client.delete_objects(
                Bucket=settings.AWS_PRIVATE_BUCKET_NAME,
                Delete={
                    'Objects': [{'Key': name}],
                    'Quiet': True
                }
            )
            return True
        except Exception as e:
          return False