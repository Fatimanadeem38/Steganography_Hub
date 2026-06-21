from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),

    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('encode/', views.encode_view, name='encode'),
    path('decode/', views.decode_view, name='decode'),
    path('activation-sent/', views.activation_sent_view, name='activation_sent'),
    path('verify-email/<uidb64>/<token>/', views.verify_email_view, name='verify_email'),
    path('manage-key/', views.manage_key_view, name='manage_key'),
    path('test-email/', views.test_email, name='test_email'),
    path("unfreeze-image/<str:token>/", views.unfreeze_image_view, name="unfreeze_image"),
    path("dip-techniques/", views.dip_techniques_view, name="dip_techniques"),
]