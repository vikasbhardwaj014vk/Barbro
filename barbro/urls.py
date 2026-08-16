from django.contrib import admin
from django.urls import path, include
from . import views

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [

    # Your existing pages
    path("", views.first_page, name="first_page"),
    path("admin/", admin.site.urls),

    # Existing customer and barber applications
    path("customer/", include("customer.urls")),
    path("barber/", include("barber.urls")),

    # JWT Authentication
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]


# from django.contrib import admin
# from django.urls import path , include
# from . import views



# urlpatterns = [
#     path("",  views.first_page , name="first_page" ),
#     path('admin/', admin.site.urls),
#     path("customer/", include("customer.urls")),
#     path("barber/", include("barber.urls")),
    
    
  
# ]