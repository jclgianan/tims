from django.contrib import admin
from .models import Ticket, SupportTicket, PrintingTicket
# Register your models here.

admin.site.register(SupportTicket)
admin.site.register(PrintingTicket)