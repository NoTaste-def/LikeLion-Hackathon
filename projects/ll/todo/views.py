from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets
from .models import TodoItem, TodoItemDate
from .serializers import TodoItemSerializer, TodoItemDateSerializer
from django.db.models import Count

class TodoItemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TodoItem.objects.all()
    serializer_class = TodoItemSerializer

class TodoItemDateViewSet(viewsets.ModelViewSet):
    queryset = TodoItemDate.objects.all()
    serializer_class = TodoItemDateSerializer

class CalendarReadAPIView(APIView):
    def get(self, request, item_name, format=None):
        try:
            item = TodoItem.objects.get(name=item_name)
        except TodoItem.DoesNotExist:
            return Response({'detail': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)
        
        dates = TodoItemDate.objects.filter(item=item).values_list('date', flat=True)
        return Response({'item': item_name, 'dates': list(dates)})

class CalendarCountAPIView(APIView):
    def get(self, request, format=None):
        date_counts = (
            TodoItemDate.objects
            .values('date')
            .annotate(count=Count('date'))
            .order_by('date')
        )
        return Response({'date_counts': list(date_counts)})
