from django.shortcuts import render

# Create your views here.


def eval(request):
    return render(request, 'koodam/index.html')
