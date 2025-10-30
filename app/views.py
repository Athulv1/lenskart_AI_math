from django.shortcuts import render

# Create your views here.


def demo_view(request):
    """Serve the demo HTML frontend"""
    return render(request, 'demo.html')
