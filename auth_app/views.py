# Create your views here.
# Create your views here.

from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import generic
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from .forms import AppUserCreationForm, AppUserLoginForm


class SignUpView(generic.CreateView):
    form_class = AppUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'accounts/signup.html'


def login_view(request):
    if request.method == 'POST':
        form = AppUserLoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # or where you want to redirect
            else:
                return render(request, 'accounts/login.html', {'form': form, 'error': 'Invalid credentials'})
    else:
        form = AppUserLoginForm()
    return render(request, 'accounts/login.html', {'form': form})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_view(request):
    print(permission_classes)

    if request.method == 'POST':
        return HttpResponse("<h1>Page was found</h1>")

    else:
        return HttpResponse("<h1>Page was found</h1>")
