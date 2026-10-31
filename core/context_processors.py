def global_context(request):
    try:
        from movies.models import Genre
        genres = list(Genre.objects.all()[:8])
    except Exception:
        genres = []

    cities = ['Kochi', 'Bengaluru', 'Mumbai', 'Delhi-NCR', 'Hyderabad']
    current_city = request.GET.get('city') or request.session.get('selected_city') or 'Kochi'
    request.session['selected_city'] = current_city

    return {
        'SITE_NAME': 'CINEVERSE',
        'CITIES': cities,
        'CURRENT_CITY': current_city,
        'NAV_GENRES': genres,
    }
