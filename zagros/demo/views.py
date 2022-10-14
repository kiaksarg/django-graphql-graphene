from django.shortcuts import render
from django.http import HttpResponse

# from zagros.core.permissions import ProductPermissions
# from ..core.permissions import ProductPermissions


def home(request):
    return HttpResponse(f'''
    <h1>Demo Home
    <br />
    # Product Permssion:
     </h1>''')
