from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
class InventoryItem(models.Model):
    inventory_id = models.CharField(max_length=50, unique=True)
    item_name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    processor = models.CharField(max_length=255, blank=True, null=True)
    ram = models.CharField(max_length=100, blank=True, null=True)
    storage = models.CharField(max_length=100, blank=True, null=True)
    graphics_card = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=50)
    condition = models.CharField(max_length=50)
    issued_to = models.CharField(max_length=255, blank=True, null=True)
    office = models.CharField(max_length=255, blank=True, null=True)
    date_acquired = models.DateField(blank=True, null=True)
    date_issued = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.inventory_id} - {self.item_name}"

