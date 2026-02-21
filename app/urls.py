# urls.py - O'ZGARTIRILGAN VERSIYA
from django.contrib import admin
from django.urls import path
from .views import (
    index, create_order, clients, sozlamalar, update_order_status, 
    delete_order, boshqaruv, profile_view, video_rasim, add_video, 
    add_photo, delete_video, delete_photo, delete_media, photo_list, 
    baraban, spin_baraban, sovga_management, foydalanuvchilar_list, 
    update_yutuq, get_yutuq_info, mark_yutuq_used, foydalanuvchi_detail,
    get_review_stats, get_review, delete_review, edit_review, add_review, 
    reviews_list, active_ads, ad_detail, create_ad
)

urlpatterns = [
    path('', index, name='index'),
    path('create_order/', create_order, name='create_order'),
    path('clients/', clients, name='clients'),
    path('sozlamalar/', sozlamalar, name='sozlamalar'),
    path('boshqaruv/', boshqaruv, name='boshqaruv'),           
    path('order/<int:order_id>/update-status/', update_order_status, name='update_order_status'),
    path('profile/', profile_view, name='profile'),
    path('media/', video_rasim, name='video_rasim'),
    path('media/<int:pk>/', video_rasim, name='edit_media'),
    path('order/<int:order_id>/delete/', delete_order, name='delete_order'),
    path('media/delete/<int:pk>/', delete_media, name='delete_media'),

    # Video uchun
    path('videos/', add_video, name='video_list'),
    path('videos/add/', add_video, name='add_video'),
    path('videos/edit/<int:pk>/', add_video, name='edit_video'),
    path('videos/delete/<int:pk>/', delete_video, name='delete_video'),
    
    # Rasm uchun
    path('photos/', photo_list, name='photo_list'),
    path('photos/add/', add_photo, name='add_photo'),
    path('photos/edit/<int:pk>/', add_photo, name='edit_photo'),
    path('photos/delete/<int:pk>/', delete_photo, name='delete_photo'),
    
    # Umumiy media o'chirish
    path('media/delete/<int:pk>/', delete_media, name='delete_media'),
    
    # Baraban uchun
    path('baraban/', baraban, name='baraban'),
    path('baraban/spin/', spin_baraban, name='spin_baraban'),
    path('sovga-boshqarish/', sovga_management, name='sovga_management'),

    # ADMIN PANEL UCHUN (BOSHQA PREFIX ISHLATING)
    path('dashboard/foydalanuvchilar/', foydalanuvchilar_list, name='foydalanuvchilar_list'),
    path('dashboard/foydalanuvchi/<int:user_id>/', foydalanuvchi_detail, name='foydalanuvchi_detail'),
    path('dashboard/get-yutuq/<int:yutuq_id>/', get_yutuq_info, name='get_yutuq_info'),
    path('dashboard/update-yutuq/', update_yutuq, name='update_yutuq'),
    path('dashboard/mark-used/<int:yutuq_id>/', mark_yutuq_used, name='mark_yutuq_used'),

    # Sharx
    path('reviews/', reviews_list, name='reviews_list'),
    path('api/add-review/', add_review, name='add_review'),
    path('api/edit-review/<int:review_id>/', edit_review, name='edit_review'),
    path('api/delete-review/<int:review_id>/', delete_review, name='delete_review'),
    path('api/get-review/<int:review_id>/', get_review, name='get_review'),
    path('api/review-stats/', get_review_stats, name='review_stats'),
    
    # Django admin uchun
    path('admin/', admin.site.urls),

    path('ads/', active_ads, name='ads'),
    path('ads/<int:pk>/', ad_detail, name='ad_detail'),
    path("ads/create/", create_ad, name="create_ad"),

]