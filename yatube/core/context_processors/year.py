from datetime import datetime


def year(request):
    current_year = datetime.now()
    return {
        'year': current_year.year,
    }
