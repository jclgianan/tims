from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Ticket(models.Model):
    name = models.CharField(max_length=100)
    office_name = models.CharField(max_length=100)
    receiving_date = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True)
    release_date = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.id} - {self.note} ({self.name})"
    
class SupportTicket(Ticket):
    SUPPORT_CHOICES = [
        ('for_approval', 'For Approval'),
        ('pending', 'Pending'),
        ('ongoing', 'Ongoing'),
        ('resolved', 'Resolved'),
        ('unrepairable', 'Unrepairable'),
        ('cancelled', 'Cancelled'),
    ]
    
    device_id = models.CharField(max_length=10, unique=True, default='0')
    status = models.CharField(max_length=20, choices=SUPPORT_CHOICES, default='pending')
    item_name = models.CharField(max_length=100)
    issue = models.TextField(max_length=255)
    solution = models.TextField(max_length=255)
    
    
class PrintingTicket(Ticket):
    PRINT_CHOICES = [
        ('for_approval', 'For Approval'),
        ('pending', 'Pending'),
        ('ongoing', 'Ongoing'),
        ('printed', 'Printed'),
        ('released', 'Released'),
        ('cancelled', 'Cancelled'),
    ]
    title = models.CharField(max_length=100, default="n/a")
    status = models.CharField(max_length=20, choices=PRINT_CHOICES, default='pending')
    height = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    width = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    quantity = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    deadline = models.DateTimeField(auto_now_add=True)
    file_link = models.CharField(max_length=100, default="n/a")
    
    