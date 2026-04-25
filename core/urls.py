from django.urls import path
from . import views
from .views import get_career_roadmap, home, roadmap

urlpatterns = [
    path('', views.home, name='home'),
    path('roadmap/', views.roadmap, name='roadmap'),

    path('signin/', views.sign_in, name='sign_in'),
    path('signup/', views.sign_up, name='sign_up'),
    path('my-progress/', views.my_progress, name='my_progress'),
    path("toggle-progress/<int:step_id>/", views.toggle_progress, name="toggle_progress"),
    path("api/career-roadmap/", get_career_roadmap, name="career-roadmap"),
    path("roadmap/pdf/", views.roadmap_pdf, name="roadmap_pdf"), 
    path("profile/", views.profile, name="profile"),
    


]
