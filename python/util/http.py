from django.http import HttpResponse


def create_file_response(data: bytes, filename: str, content_type: str) -> HttpResponse:
    """
    Returns a downloadable http response from the provided data
    :param data: bytes containing the data to download
    :param filename: download filename
    :param content_type: download content type
    :return: Http response containing the file for download
    """
    # Prepare and return response
    response = HttpResponse(content_type=content_type)
    response['Content-Disposition'] = 'attachment; filename={}'.format(filename)
    response['Content-Length'] = len(data)
    response.write(data)
    return response
