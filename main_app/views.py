from django.shortcuts import render

import logging

logger = logging.getLogger('main_app')

def index(request):
    logger.warning("Someone accessed the index page.")
    return render(request, 'main_app/home.html')
