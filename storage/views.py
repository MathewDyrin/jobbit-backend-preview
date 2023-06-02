from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from django.core.files.uploadedfile import TemporaryUploadedFile
from .storages import FileStorage


class StorageException(Exception):
    pass


class Storage(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def validate(self, file: TemporaryUploadedFile):
        storage_settings = getattr(settings, 'STORAGE', '')

        # Type validation
        if file.content_type not in storage_settings.get('ALLOWED_TYPES'):
            raise StorageException(f'Media type `{file.content_type}` not allowed')

        # Size validation
        if storage_settings.get('MAX_SIZES').get(file.content_type):
            max_size = storage_settings.get('MAX_SIZES').get(file.content_type)

            if max_size < file.size:
                raise StorageException(f'Max size for media type {file.content_type} is {max_size} bytes')

    def post(self, request):
        if not request.FILES.get('file'):
            return Response({'detail': 'No files provided'}, status=status.HTTP_400_BAD_REQUEST)
        client_file = request.FILES.get('file')
        try:
            self.validate(client_file)
        except StorageException as error:
            return Response({'detail': str(error)}, status=status.HTTP_400_BAD_REQUEST)

        url = FileStorage.save(client_file, request)

        return Response({
            'filename': client_file.name,
            'size': client_file.size,
            'media_type': client_file.content_type,
            'url': url
        })
