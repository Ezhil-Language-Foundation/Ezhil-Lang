from django.shortcuts import render
from django.shortcuts import render_to_response

# Create your views here.
def evaluate( request ):
    return render_to_response("cannot do anything at this moment")

# query about state of the program
def query(request,job):
    return render_to_response("cannot query job "+job+" at this moment")

# query about state of the program
def result(request,job):
    return render_to_response("cannot find result of job "+job+" at this moment")

# query about state of the program
def delete_qjob(request,job):
    return render_to_response("cannot delete job "+job+" at this moment")
