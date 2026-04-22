from django.shortcuts import render

def book_for_patient(request):
    return render(request, "receptionist/book_for_patient.html")

def dashboard(request):
    return render(request, "receptionist/dashboard.html")