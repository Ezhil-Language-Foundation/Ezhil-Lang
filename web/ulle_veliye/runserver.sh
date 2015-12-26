#!/bin/bash
pip install -r requirements.txt
exec ./manage.py runserver 0.0.0.0:8000
