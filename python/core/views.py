import os
from base64 import b64encode
from io import BytesIO

from PIL import Image, ImageFilter
from django.http import HttpResponse, HttpRequest, JsonResponse, Http404
from django.shortcuts import render, get_object_or_404

from core.models import BeadColor, ImageSession, BeadBrand
from pixel.settings import PDF_TEXT
from util.general import generate_session_key, create_tmp_file
from util.http import create_file_response
from util.image import downsample, remap, upsample, preserve_aspect_ratio
from util.pdf import VALID_COLOR_CODES, PDFGenerator


def index(request: HttpRequest) -> HttpResponse:
    """
    Home page. Provides user the ability to upload a file.
    """
    return render(request, 'core/index.html')


def upload(request: HttpRequest) -> JsonResponse:
    """
    Handles file upload and returns a unique session key
    """
    error = None
    try:
        file = request.FILES.get('file')
        key = generate_session_key()
        tmp_file = create_tmp_file(file)
        ImageSession.objects.create(session_key=key, src_file=tmp_file)
    except Exception as e:
        error = str(e)
        key = None
    return JsonResponse({'error': error, 'key': key})


def process(request: HttpRequest) -> HttpResponse:
    """
    Processes the image with the given parameters
    """

    # Get the session key from the GET params
    key = request.GET.get('key', None)
    image_session = get_object_or_404(ImageSession, pk=key)

    # Load the image from disk
    image = Image.open(image_session.src_file)

    # Downsample the image to a reasonable size for previews
    src_image = downsample(image, 512, 512)

    # Extract processing parameters from POST data
    dest_width = int(request.POST.get('width', 64))
    dest_height = int(request.POST.get('height', 64))
    dest_width, dest_height = preserve_aspect_ratio(image.width, image.height, dest_width, dest_height)
    blur = request.POST.get('blur', '0') == '1'
    sharpen = request.POST.get('sharpen', '0') == '1'
    selected_colors = list(
        map(int, request.POST.getlist('colors', BeadColor.objects.all().values_list('id', flat=True))))
    if len(selected_colors) > 0:
        available_colors = BeadColor.objects.filter(id__in=selected_colors)
    else:
        available_colors = BeadColor.objects.all()

    # Apply filters if applicable
    if blur:
        src_image = src_image.filter(ImageFilter.BLUR)
    elif sharpen:
        src_image = src_image.filter(ImageFilter.SHARPEN)

    # Convert src image to base64
    with BytesIO() as buffer:
        src_image.save(buffer, 'png')
        src_data = b64encode(buffer.getvalue())

    # Perform the image -> sprite process:
    # 1) Downsample to the desired size (1 px per bead)
    # 2) Remap the colors to the available bead colors
    # 3) Upsample to a reasonable viewing size
    px_image = downsample(src_image, dest_width, dest_height)
    remapped_image = remap(px_image, available_colors)
    px_image = upsample(remapped_image, 512, 512)

    # Convert image data to base64 for page display
    with BytesIO() as buffer:
        px_image.save(buffer, 'png')
        px_data = b64encode(buffer.getvalue())

    # Save remapped image for possible download
    processed_file = create_tmp_file()
    remapped_image.save(processed_file, 'png')
    image_session.processed_file = processed_file
    image_session.save()

    color_groups = {brand.name: list(BeadColor.objects.filter(brand=brand)) for brand in BeadBrand.objects.all()}

    return render(request, 'core/process.html', {
        'src': src_data,
        'px': px_data,
        'width': dest_width,
        'height': dest_height,
        'blur': 1 if blur else 0,
        'sharpen': 1 if sharpen else 0,
        'color_groups': color_groups,
        'selected_colors': selected_colors,
        'aspect_ratio': image.width / image.height
    })


def download(request: HttpRequest) -> HttpResponse:
    # Extract the session key from the GET params
    session_key = request.GET.get('key', None)
    image_session = get_object_or_404(ImageSession, pk=session_key)

    # Make sure file exists
    fp = image_session.processed_file
    if fp is None or not os.path.isfile(fp):
        raise Http404

    # Extract the pixel data in row-major order
    image = Image.open(fp)
    px_data = [image.getpixel((x, y)) for y in range(image.height) for x in range(image.width)]

    # Create the color code -> color name mapping
    color_map = {VALID_COLOR_CODES[i]: str(bead_color) for (i, bead_color) in enumerate(BeadColor.objects.all())}
    inverse_color_map = {v: k for (k, v) in color_map.items()}

    # Map the pixel data to the bead colors
    bead_map = {(bead.red, bead.green, bead.blue): inverse_color_map[str(bead)] for bead in BeadColor.objects.all()}
    px_data = [bead_map[tuple(rgba[:3])] for rgba in px_data]

    # Generate the PDF
    pdf_gen = PDFGenerator(color_map, px_data, image.width, text=[PDF_TEXT['THANK_YOU'], PDF_TEXT['INSTRUCTIONS']])
    pdf_bytes = pdf_gen.generate_pdf()

    # Return the file for download
    return create_file_response(pdf_bytes, 'bead_template.pdf', 'application/pdf')
