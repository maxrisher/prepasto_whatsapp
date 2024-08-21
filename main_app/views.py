from django.http import HttpResponse

import logging

logger = logging.getLogger('main_app')

def index(request):
    logger.warning("Someone accessed the index page.")
    return HttpResponse("Hello chickpea and garlic world!")
