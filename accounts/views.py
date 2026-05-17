from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render


def login_view(request):
    error = ""
    if request.method == "POST":
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            return redirect("dashboard")
        error = "Accès réservé aux administrateurs."

    return render(request, "accounts/login.html", {"error": error})


def register_view(request):
    return redirect("login")


def logout_view(request):
    logout(request)
    return redirect("home")

# Create your views here.
