from django.shortcuts import render, redirect 
from django.http import HttpResponse


def first_page(request):
    return render(request, "first_page.html")