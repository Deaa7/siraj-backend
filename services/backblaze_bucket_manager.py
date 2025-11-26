

# should return the path of file 
def upload_file_to_bucket(file ):
 pass
#   s3= boto3.client(service_name='s3' ,
#                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
#                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
#                    endpoint_url=settings.ENDPOINT_URL,
#                    region_name=settings.REGION_NAME,
#                    config=Config(signature_version='s3v4')
# )
# #   print('here 1' , s3) 
#   s3.upload_fileobj(file , bucket_name , file.name ,ExtraArgs={'ContentType':file.content_type})
#   bucket_location = s3.get_bucket_location(Bucket=bucket_name)
# #   print('here 2' , bucket_location)
#   region = bucket_location['LocationConstraint']
# #   print('here 3' , region)
#   # file_url = "https://s3.eu-central-003.backblazeb2.com/syrian-virtual-institution/" + file.name
#   file_url = "https://syrian-virtual-institution.s3.eu-central-003.backblazeb2.com/" + file.name
#   return file_url


def get_file_url_from_bucket(file_name ):
    pass
    #     try:
    #     obj = Notes.objects.get(id = id) 
        
    #     # Extract the file key from the stored URL
    #     # The content field stores: https://syrian-virtual-institution.s3.eu-central-003.backblazeb2.com/filename.pdf
    #     # We need just the filename part
    #     if obj.content and obj.content.startswith('https://'):
    #         file_key = obj.content.split('/')[-1]  # Get the filename from the URL
    #     else:
    #         file_key = obj.content  # If it's already just a filename
        
    #     print(f"File key: {file_key}")
        
    #     s3_client = boto3.client(
    #         's3',
    #         endpoint_url=settings.ENDPOINT_URL,
    #         aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    #         aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    #         region_name=settings.REGION_NAME,
    #         config=Config(signature_version='s3v4', region_name=settings.REGION_NAME)
    #     )
        
    #     # First, check if the file exists
    #     try:
    #         s3_client.head_object(Bucket=settings.BUCKET_NAME, Key=file_key)
    #         print(f"File exists in bucket: {file_key}")
    #     except Exception as head_error:
    #         print(f"File not found in bucket: {file_key}")
    #         print(f"Head error: {str(head_error)}")
    #         return Response({'error': 'File not found in storage', 'file_key': file_key}, status=404)
        
    #     # Generate presigned URL for private bucket
    #     # For Backblaze B2, we need to be more specific about the parameters
    #     try:
    #         presigned_url = s3_client.generate_presigned_url(
    #             'get_object',
    #             Params={
    #                 'Bucket': settings.BUCKET_NAME,
    #                 'Key': file_key,
    #             },
    #             ExpiresIn=15  # 1 hour expiration
    #         )
            
    #         print(f"Generated presigned URL: {presigned_url[:100]}...")
    #         return Response({'content': presigned_url})
            
    #     except Exception as url_error:
    #         print(f"Error generating presigned URL: {str(url_error)}")
    #         print(f"Error type: {type(url_error).__name__}")
    #         return Response({'error': 'File not found in storage', 'file_key': file_key}, status=404)
  
    # except Exception as e:
    #     print(f"Error generating presigned URL: {str(e)}")
    #     print(f"Error type: {type(e).__name__}")
    #     return Response({'error': str(e), 'error_type': type(e).__name__}, status=500)


# services.py
from django.core.files.storage import default_storage

def delete_file_from_b2(file_path):
    """
    Delete a file from Backblaze B2 using its stored path
    """
    try:
        # This is the key line - uses the path from your database
            default_storage.delete(file_path)

            return True  # File doesn't exist, consider it "deleted"
            
    except Exception as e:
        return False
