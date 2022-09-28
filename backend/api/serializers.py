from rest_framework import serializers
from .models import Aadhaar, AadhaarImg


class AadharSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aadhaar
        fields = '__all__'
        read_only_fields = ['id']
        extra_kwargs = {
            'id': {'read_only': True}
        }


class AadhaarImgSerializer(serializers.ModelSerializer):
    class Meta:
        model = AadhaarImg
        fields = '__all__'
