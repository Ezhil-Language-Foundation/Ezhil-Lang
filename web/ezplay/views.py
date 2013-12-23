from django.shortcuts import render, render_to_response

# Create your views here.

def evaluate( request ):
    if request.method == "POST":
        return render_to_response("evaluating code")
    
    return render_to_response("providing you with the form")

def save( request, prefix ):
    return render_to_response("cannot save "+prefix+" at this moment")

def download( request, prefix ):
    return render_to_response("cannot download "+prefix+" at this moment")

def lookupp( request, prefix ):
    return render_to_response("cannot lookup "+prefix+" at this moment")
