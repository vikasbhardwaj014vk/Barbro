from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import redirect


class Barber(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    shop_name = models.CharField(max_length=200)

    phone = models.CharField(max_length=15)

    address = models.TextField()

    experience = models.IntegerField()

    

    

   

    def __str__(self):
        return self.shop_name



def barber_signup(request):

    if request.method == "POST":

        username=request.POST["username"]

        email=request.POST["email"]

        password=request.POST["password"]

        shop=request.POST["shop_name"]

        phone=request.POST["phone"]

        user = User.objects.create_user(

            username=username,

            email=email,

            password=password

        )

        Barber.objects.create(

            user=user,

            shop_name=shop,

            phone=phone,

        )

        return redirect("barber_login")


# class Barber(models.Model):

#     user = models.OneToOneField(User,on_delete=models.CASCADE)

#     shop_name = models.CharField(max_length=200)

#     phone = models.CharField(max_length=15)

#     address = models.TextField()

#     experience = models.IntegerField()

#     is_open = models.BooleanField(default=True)

#     def __str__(self):
#         return self.shop_name