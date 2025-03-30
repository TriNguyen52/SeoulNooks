from django.urls import path
from . import views

urlpatterns = [
    path('new-application/', views.applications, name='new_application'),
    path('list/', views.applications_list, name='applications_list'),
    path('', views.applications, name='applications'),
    path('detail/<int:pk>/', views.application_detail, name='application_detail'),
    path('edit/<int:pk>/', views.edit_application, name='edit_application'),
    path('application/step2/', views.application_step2, name='application_step2'),
    path('success/', views.application_success, name='application_success'),
    path('available-chapters/', views.available_chapters, name='available_chapters'),
    # API endpoints
    path('check-availability/', views.check_availability, name='check_availability'),
    path('create/', views.create_application, name='create_application'),
    path('apply-coupon/', views.apply_coupon, name='apply_coupon'),
]
