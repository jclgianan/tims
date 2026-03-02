from django.shortcuts import render

# Create your views here.
from .models import PrintingTicket, SupportTicket, Ticket

def all_tickets_list(request):
    tickets = Ticket.objects.all().order_by('-id')
    
    return render(request, 'tickets/ticket_list.html', {'tickets': tickets})

def printing_ticket_list(request):
    tickets = PrintingTicket.objects.all().order_by('-id') 
    
    return render(request, 'tickets/print_list.html', {'tickets': tickets})

def support_ticket_list(request):
    tickets = SupportTicket.objects.all().order_by('-id') 
    
    return render(request, 'tickets/support_list.html', {'tickets': tickets})
