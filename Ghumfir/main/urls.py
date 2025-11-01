from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path('login/', views.loginPage, name="login"),
    path('signup/', views.signupPage, name="signup"),
    path('logout/', views.logoutPage, name="logout"),

    path('home/', views.dashboard, name='dashboard'),

    path('memory-capsule/', views.memoryCapsule, name="memory_capsule"),

    path('add-memory/', views.add_memory, name="add_memory"),

    path('upload-sos-video/', views.upload_sos_video, name='upload_sos_video'),
    path('user-profile/', views.updateProfile, name="user_profile"),

    path('become-guide/', views.become_guide, name="become_guide"),
    path('guide-listing/', views.guideListing, name="guide_listing"),

    path('guide-profile/<str:pk>/', views.guideProfile, name="guide_profile"),

    path('places/<int:pk>/', views.place_detail, name='place_detail'),
]