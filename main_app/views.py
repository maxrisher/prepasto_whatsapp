from django.shortcuts import render

import logging

logger = logging.getLogger('main_app')

def index(request):
    logger.warning("Someone accessed the index page.")
    return render(request, 'main_app/home.html')

# Login screen / authentication

# Password, phone number, and timezone change

# dashboard / list of days view (shows summary stats, stats for current day, endless scroll of past days)

# day view (shows all meals in a given day for a user)
