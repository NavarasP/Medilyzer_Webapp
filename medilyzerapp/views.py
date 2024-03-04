from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Prescription, Upload_Image
from .ocr_main import recognize_and_compare
from PIL import Image
import io
from django.core.files.base import ContentFile

def home_view(request):
    if request.method == "GET":
        return render(request, "index.html")

def convert(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            datas = Prescription()
            upload = Upload_Image()
            datas.user = request.user 
            upload.user = request.user 
            if 'image' in request.FILES:
                image = request.FILES['image']
                upload.image = image
                upload.save()
                image_path = upload.image.path

                image_array = recognize_and_compare(image_path)

                cv_image = Image.fromarray(image_array)
                image_io = io.BytesIO()
                cv_image.save(image_io, format='JPEG')

                image_content = ContentFile(image_io.getvalue(), name=image.name)
                datas.image = image_content

            datas.save()
            image_url = datas.image.url
            print(image_url)
            return render(request, 'convert.html', {'image_url': image_url})
        else:
            messages.error(request, "Please login to convert prescription!")
            return redirect('login')
    else:
        return render(request, 'convert.html')


def base(request):
    return render(request, 'base.html')

def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

