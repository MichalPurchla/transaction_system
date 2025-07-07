from django.utils.dateparse import parse_date


def parse_date_range(request):
    from_date_str = request.GET.get("from")
    to_date_str = request.GET.get("to")
    from_date = parse_date(from_date_str) if from_date_str else None
    to_date = parse_date(to_date_str) if to_date_str else None
    return from_date, to_date
