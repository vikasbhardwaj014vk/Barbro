from django.urls import path , include
from . import views


urlpatterns = [
    
    path("signup/", views.signup, name="signup"),
    path("login_view/", views.login_view, name="login_view"),
    path("users/", views.users, name="users"),
    path("my_bookings/", views.my_bookings, name="my_bookings"),
    path("home/", views.home, name="home"),
    path("book_appointment/",views.book_appointment,name="book_appointment"),
    path("choose_barber/",views.choose_barber,name="choose_barber"),
    path("edit_appointment/<int:id>/",views.edit_appointment,name="edit_appointment"),
    path("cancel_appointment/<int:id>/",views.cancel_appointment,name="cancel_appointment"),
    path("home_service/",views.home_service,name="home_service"),
    path("book_home_service/",views.book_home_service,name="book_home_service"),
    path("faceshape/", include("faceshape.urls")),
    

]