from django.shortcuts import render
from django.http import JsonResponse
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

def add_ticket_ajax(request):
    if request.method == "POST":
        customer = request.POST.get('customer_name')
        t_type = request.POST.get('ticket_type')
        desc = request.POST.get('description')
        r_date = request.POST.get('release_date') or None
        
        # Create the ticket object
        ticket = Ticket.objects.create(
            customer_name=customer,
            ticket_type=t_type,
            description=desc,
            release_date=r_date,
            status='Pending' # Default status
        )
        
        return JsonResponse({"status": "success", "message": f"Ticket #{ticket.id} created!"})
    return JsonResponse({"status": "error"}, status=400)
