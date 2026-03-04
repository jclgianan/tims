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

def add_ticket_printing(request):
    if request.method == 'POST':
        new_print_ticket = PrintingTicket.objects.create(
            ##parent
            name=request.POST.get('name'),
            office_name=request.POST.get('office_name'),
            
            ##child
            title=request.POST.get('title'),
            width=request.POST.get('width'),
            height=request.POST.get('height'),
            quantity=request.POST.get('quantity')
        )
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


def printing_tickets_json(request):
    tickets = PrintingTicket.objects.all().order_by('-id')
    data = []
    
    for t in tickets:
        data.append({
            "id": t.id,
            "receiving_date": t.receiving_date.strftime("%Y-%m-%d %H:%M"),
            "name": t.name,
            "office": t.office_name,
            "title": t.title,
            "size": f"{float(t.width)} x {float(t.height)} ft",
            "quantity": str(t.quantity),
            "deadline": t.deadline.strftime("%Y-%m-%d %H:%M") if t.deadline else "N/A",
            "file": t.file_link,
            "release_date": t.release_date.strftime("%Y-%m-%d %H:%M") if t.release_date else "N/A",
            "status": t.get_status_display(),
        })
    return JsonResponse({'data': data})
