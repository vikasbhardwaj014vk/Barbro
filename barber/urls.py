
from django.urls import path
from . import views


urlpatterns = [
   
           path("barber_dashboard/",views.barber_dashboard, name="barber_dashboard"),
           path("barber_signup/",views.barber_signup, name="barber_signup"),
           path("barber_login/",views.barber_login, name="barber_login"),
           path("accept_appointment/<int:id>/",views.accept_appointment,name="accept_appointment",),
           path("reject_appointment/<int:id>/",views.reject_appointment,name="reject_appointment",),
           path("accept_home_service/<int:id>/",views.accept_home_service,name="accept_home_service"),
           path("reject_home_service/<int:id>/",views.reject_home_service,name="reject_home_service"),

]
