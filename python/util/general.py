import os
import uuid

from django.core.files.uploadedfile import UploadedFile

from pixel.settings import TMP_DIR


def generate_session_key():
    return str(uuid.uuid4())


def create_tmp_file(buffer=None):
    file_name = os.path.join(TMP_DIR, str(uuid.uuid4()))
    if buffer is not None:
        if isinstance(buffer, UploadedFile):
            buffer = buffer.file
        with open(file_name, 'wb') as fout:
            fout.write(buffer.read())
    return file_name
