from django.shortcuts import render


def error_404(request, exception):
    return render(request, 'page_404.html')


def error_500(request):
    return render(request, 'page_500.html')
