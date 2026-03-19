import os
import boto3
from botocore.config import Config
from dotenv import load_dotenv

load_dotenv()

class R2Storage:
    def __init__(self):
        self.access_key = os.getenv("R2_ACCESS_KEY_ID")
        self.secret_key = os.getenv("R2_SECRET_ACCESS_KEY")
        self.endpoint_url = os.getenv("R2_ENDPOINT_URL")
        self.bucket_name = os.getenv("R2_BUCKET_NAME")
        
        if all([self.access_key, self.secret_key, self.endpoint_url]):
            self.s3_client = boto3.client(
                's3',
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                config=Config(signature_version='s3v4')
            )
        else:
            self.s3_client = None

    def upload_file(self, file_path, object_name=None):
        """Upload a file to R2 bucket"""
        if not self.s3_client:
            return False
            
        if object_name is None:
            object_name = os.path.basename(file_path)

        try:
            self.s3_client.upload_file(file_path, self.bucket_name, object_name)
            return f"{self.endpoint_url}/{self.bucket_name}/{object_name}"
        except Exception as e:
            print(f"Error uploading to R2: {e}")
            return False

    def get_download_url(self, object_name, expiration=3600):
        """Generate a presigned URL for the R2 object"""
        if not self.s3_client:
            return None
            
        try:
            response = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': object_name},
                ExpiresIn=expiration
            )
            return response
        except Exception as e:
            print(f"Error generating presigned URL: {e}")
            return None

storage = R2Storage()
