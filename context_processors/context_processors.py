import datetime as dt


def year(request):
    years = dt.datetime.today().year
    return {
        "year": years,
    }