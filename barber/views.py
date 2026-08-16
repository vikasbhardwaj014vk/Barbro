from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout 
from .models import Barber
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Barber
from customer.models import Appointment , HomeService
from django.core.validators import validate_email
from django.core.exceptions import ValidationError



# ==============================
# Barber Signup
# ==============================
def barber_signup(request):

    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        shop_name = request.POST.get("shop_name")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        experience = request.POST.get("experience")

        # Validate email format
        try:
            validate_email(email)
        except ValidationError:
            return render(request, "barber_signup.html", {
                "error": "Please enter a valid email address."
            })

        # Check username
        if User.objects.filter(username=username).exists():
            return render(request, "barber_signup.html", {
                "error": "Username already exists."
            })

        # Check email
        if User.objects.filter(email=email).exists():
            return render(request, "barber_signup.html", {
                "error": "Email already registered."
            })

        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # Create barber profile
        Barber.objects.create(
            user=user,
            shop_name=shop_name,
            phone=phone,
            address=address,
            experience=experience
        )

        return redirect("barber_login")

    return render(request, "barber_signup.html")

# def barber_signup(request):

#     if request.method == "POST":

#         username = request.POST.get("username")
#         email = request.POST.get("email")
#         password = request.POST.get("password")
#         shop_name = request.POST.get("shop_name")
#         phone = request.POST.get("phone")
#         address = request.POST.get("address")
#         experience = request.POST.get("experience")

#         # Check if username already exists
#         if User.objects.filter(username=username).exists():

#             return render(request, "barber_signup.html", {
#                 "error": "Username already exists."
#             })

#         # Check if email already exists
#         if User.objects.filter(email=email).exists():

#             return render(request, "barber_signup.html", {
#                 "error": "Email already registered."
#             })

#         # Create Django User
#         user = User.objects.create_user(
#             username=username,
#             email=email,
#             password=password
#         )

#         # Create Barber Profile
#         Barber.objects.create(
#             user=user,
#             shop_name=shop_name,
#             phone=phone,
#             address=address,
#             experience=experience
#         )

#         return redirect("barber_login")

#     return render(request, "barber_signup.html")


# ==============================
# Barber Login
# ==============================

def barber_login(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            # Check if this user is a registered barber
            if Barber.objects.filter(user=user).exists():

                login(request, user)

                return redirect("barber_dashboard")

            else:

                return render(request, "barber_login.html", {
                    "error": "This account is not registered as a barber.",
                    "username": username
                })

        else:

            return render(request, "barber_login.html", {
                "error": "Invalid username or password.",
                "username": username
            })

    return render(request, "barber_login.html")



def barber_logout(request):

    logout(request)

    return redirect("barber_login")


@login_required
def barber_dashboard(request):

    barber = Barber.objects.get(
        user=request.user
    )

    appointments = Appointment.objects.filter(
        barber=barber
    )

    home_services = HomeService.objects.filter(
        barber=barber
    )

    return render(
        request,
        "barber_home.html",
        {
            "appointments": appointments,
            "home_services": home_services,
        }
    )



# @login_required
# def barber_dashboard(request):

#     barber=Barber.objects.get(
#         user=request.user
#     )

#     appointments=Appointment.objects.filter(
#         barber=barber
#     )

#     return render(
#         request,
#         "barber_home.html",
#         {
#             "appointments":appointments
#         }
#     )

def accept_appointment(request,id):

    appointment=Appointment.objects.get(id=id)

    appointment.status="Accepted"

    appointment.save()

    return redirect("barber_dashboard")


def reject_appointment(request,id):

    appointment=Appointment.objects.get(id=id)

    appointment.status="Rejected"

    appointment.save()

    return redirect("barber_dashboard")

@login_required
def accept_home_service(request, id):

    service = get_object_or_404(
        HomeService,
        id=id
    )

    service.status = "Accepted"
    service.save()

    return redirect("barber_dashboard")


@login_required
def reject_home_service(request, id):

    service = get_object_or_404(
        HomeService,
        id=id
    )

    service.status = "Rejected"
    service.save()

    return redirect("barber_dashboard")


