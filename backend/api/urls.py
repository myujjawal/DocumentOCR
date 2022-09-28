from django.urls import path
from . import views

urlpatterns = [path('aadhar/', views.AadharList.as_view()),
               path('aadharimg/', views.AadhaarImgList.as_view(),
                    name='aadhaarimg_list'),
               ]
