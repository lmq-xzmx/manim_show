from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('generate-animation/', views.generate_animation, name='generate_animation'),
    path('system-prompts/', views.system_prompt_list, name='system_prompt_list'),
    path('system-prompts/add/', views.add_system_prompt, name='add_system_prompt'),
    path('system-prompts/<int:prompt_id>/toggle/', views.toggle_system_prompt, name='toggle_system_prompt'),
    path('system-prompts/<int:prompt_id>/edit/', views.edit_system_prompt, name='edit_system_prompt'),
    path('system-prompts/<int:prompt_id>/delete/', views.delete_system_prompt, name='delete_system_prompt'),
    path('system-prompts/active/', views.get_active_system_prompt, name='get_active_system_prompt'),
] 