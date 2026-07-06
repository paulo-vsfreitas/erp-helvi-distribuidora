from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def dashboard_compras(request):
    return render(request, "compras/dashboard.html")