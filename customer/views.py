from django.shortcuts import render
from django.contrib.auth.models import User
from django.shortcuts import render, redirect 
from django.http import HttpResponse
from django.contrib.auth import authenticate, login 
from barber.models import Barber
from .models import Appointment , HomeService
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate( request, username=username,password=password )

        if user is not None:
            login(request, user)      # Create session
            print("Login Successful")
            return redirect("home")  # Redirect to home page
        else:
             return render(request, "login.html", {
            "error": "Invalid username or password.",
            "username": username  # Preserve entered username
        })

    return render(request, "login.html")
from django.contrib.auth.models import User

def signup(request):

    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")

        if password != password2:
            return render(request, "signup.html", {
                "error": "Passwords do not match.",
                "username": username,
                "email": email,
            })

        if User.objects.filter(username=username).exists():
            return render(request, "signup.html", {
                "error": "Username already exists.",
                "username": username,
                "email": email,
            })

        if User.objects.filter(email=email).exists():
            return render(request, "signup.html", {
                "error": "Email is already registered.",
                "username": username,
                "email": email,
            })

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        return redirect("login_view")

    return render(request, "signup.html")


def users(request):
    users = User.objects.all()

    data = ""
    for user in users:
        data += f"{user.username} - {user.email}<br>"

    return HttpResponse(data)


@login_required
def book_appointment(request):

    if request.method == "POST":

        barber = get_object_or_404(
            Barber,
            id=request.POST["barber_id"]
        )

        Appointment.objects.create(
            customer=request.user,
            barber=barber,
            date=request.POST["date"],
            time=request.POST["time"],
            service=request.POST["service"]
        )

        return redirect("my_bookings ")   

    # If someone visits this URL directly
    return redirect("choose_barber")



@login_required
def home_service(request):

    barbers = Barber.objects.filter()

    return render(
        request,
        "home_service.html",
        {
            "barbers": barbers
        }
    )

@login_required
def book_home_service(request):

    if request.method == "POST":

        barber = get_object_or_404(
            Barber,
            id=request.POST["barber_id"]
        )

        HomeService.objects.create(

            customer=request.user,

            barber=barber,

            service=request.POST["service"],

            date=request.POST["date"],

            time=request.POST["time"],

            address=request.POST["address"],

            latitude=request.POST["latitude"],

            longitude=request.POST["longitude"],

            notes=request.POST["notes"],

            status="Pending"

        )

        return redirect("my_bookings")

    return redirect("home_service")

@login_required
def choose_barber(request):
    barbers = Barber.objects.select_related('user').all()

    return render(request, "bookings.html", {
        "barbers": barbers
    })


@login_required
def my_bookings(request):

    appointments = Appointment.objects.filter(
        customer=request.user
    ).select_related(
        "barber",
        "barber__user"
    )

    home_services = HomeService.objects.filter(
        customer=request.user
    ).select_related(
        "barber",
        "barber__user"
    )

    return render(
        request,
        "my_bookings.html",
        {
            "appointments": appointments,
            "home_services": home_services
        }
    )



@login_required
def edit_appointment(request, id):

    appointment = get_object_or_404(
        Appointment,
        id=id,
        customer=request.user
    )

    if request.method == "POST":

        appointment.date = request.POST["date"]
        appointment.time = request.POST["time"]
        appointment.service = request.POST["service"]

        appointment.save()

        return redirect("my_bookings")

    return render(request,"edit_appointment.html",{"appointment": appointment})


@login_required
def cancel_appointment(request, id):

    appointment = get_object_or_404(
        Appointment,
        id=id,
        customer=request.user
    )

    appointment.status = "Cancelled"
    appointment.save()

    return redirect("my_bookings")






@login_required
def home(request):
    return render(request, "home.html")


