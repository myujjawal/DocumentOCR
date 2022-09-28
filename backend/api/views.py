from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse

from .ocr import boxOCR, naiveOCR
from .models import Aadhaar, AadhaarImg
from .serializers import AadharSerializer, AadhaarImgSerializer

from rest_framework.generics import ListAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status


# Create your views here.


class AadharList(ListAPIView):
    queryset = Aadhaar.objects.all()
    serializer_class = AadharSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class AadhaarImgList(ListAPIView):
    parser_classes = (MultiPartParser, FormParser)
    queryset = AadhaarImg.objects.all()
    serializer_class = AadhaarImgSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        posts_serializer = AadhaarImgSerializer(data=request.data)
        if posts_serializer.is_valid():
            response_data = naiveOCR(request.data['image'])
            response_data2 = boxOCR(request.data)
            myresponse = {'string': response_data, 'box': response_data2}
            # boxOCR(request.FILES['image'])
            # posts_serializer.save()
            # return Response(posts_serializer.data , status=status.HTTP_201_CREATED)
            return Response(myresponse, status=status.HTTP_201_CREATED)

        else:
            print('error', posts_serializer.errors)
            return Response(posts_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def downloadfile(request):
        response_data2 = boxOCR(request.data['image'])
        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="text.txt"'
        lines = ["This is a test file"]
        response.write(lines)
        return response
