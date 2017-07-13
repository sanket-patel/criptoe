from django.shortcuts import get_object_or_404, render


def testview(request):
    return render(request, 'testingapp/testview.html')
