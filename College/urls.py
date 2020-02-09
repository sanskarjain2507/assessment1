
from django.urls import path
from . import views

urlpatterns = [

    path("login_page",views.login_page),
    path("signup_page",views.register_college),
    path("college_register_success",views.register_college_success),
    path("college_login_success",views.college_login_success),
    path("ajax/validate_email",views.validate_email),
    path("ajax/validate_college_id",views.validate_college_id),

    ]