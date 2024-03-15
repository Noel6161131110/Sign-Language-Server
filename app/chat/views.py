from rest_framework.views import APIView
from django.shortcuts import render

class MainView(APIView):
    def get(self,request):
        context = {}
        
        return render(request, 'chat/main.html', context=context)