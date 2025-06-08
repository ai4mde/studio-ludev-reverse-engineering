from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from shared_models.models import *





def homerender(request):
    context = {}
    context['user'] = request.user
    return render(request, 'shop_interface_home.html', context)