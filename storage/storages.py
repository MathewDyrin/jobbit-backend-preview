import uuid
import boto3
from transliterate import translit
from abc import ABC, abstractclassmethod
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import TemporaryUploadedFile
from rest_framework.request import HttpRequest


class IStorage(ABC):
    @abstractclassmethod
    def save(cls, *args, **kwargs) -> str:
        pass


class S3ObjectStorage(IStorage):
    @classmethod
    def save(cls, file: TemporaryUploadedFile, request: HttpRequest) -> str:
        session = boto3.session.Session()
        s3_client = session.client(
            service_name='s3',
            endpoint_url=getattr(settings, 'S3_ENDPOINT_URL', ''),
            aws_access_key_id=getattr(settings, 'S3_ACCESS_KEY_ID', ''),
            aws_secret_access_key=getattr(settings, 'S3_ACCESS_SECRET_KEY', '')
        )
        filename = translit(f'{uuid.uuid4().hex}-{file.name}', 'ru', reversed=True).replace(' ', '')
        s3_client.put_object(
            Body=file.open('rb'),
            Bucket=getattr(settings, 'S3_BUCKET_NAME', ''),
            Key=filename,
            ContentType=file.content_type
        )
        return getattr(settings, 'S3_ACCESS_URL', '') + filename


class DjangoBaseStorage(IStorage):
    @classmethod
    def save(cls, file: TemporaryUploadedFile, request: HttpRequest) -> str:
        file_name = default_storage.save(file.name, file)
        return request.build_absolute_uri(settings.MEDIA_URL + file_name)


class FileStorage:
    __mapper__ = {
        'DjangoBaseStorage': DjangoBaseStorage,
        'S3ObjectStorage': S3ObjectStorage
    }

    @classmethod
    def save(cls, file: TemporaryUploadedFile, request: HttpRequest):
        storage_settings = getattr(settings, 'STORAGE', '')
        defined_storage = storage_settings['DEFAULT_STORAGE']
        controller = cls.__mapper__.get(defined_storage)
        return controller.save(file, request)
