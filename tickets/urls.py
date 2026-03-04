from django.urls import path
from . import views

urlpatterns=[
    
    path('', views.all_tickets_list, name='ticket_list'),
    path('printing/', views.printing_ticket_list, name='printing_list'),
    path('support/', views.support_ticket_list, name='support_list'),
    path('add/', views.add_ticket_printing, name='add_ticket_ajax'),
    path('print-ticket-data/', views.printing_tickets_json, name='print_ticket_data'),
]