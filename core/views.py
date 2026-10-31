from django.shortcuts import render


def custom_404_view(request, exception=None):
    return render(request, 'core/404.html', status=404)


def custom_500_view(request):
    return render(request, 'core/500.html', status=500)
