from django.db import models

# Create your models here.
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
    