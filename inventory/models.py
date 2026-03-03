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
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sub_parts",
    )
    type = models.ForeignKey("InventoryType", on_delete=models.PROTECT, null=True)
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


class InventoryType(models.Model):
    name = models.CharField(max_length=100, unique=True)  # "Computer"
    short_name = models.CharField(max_length=10)  # "PC"
    icon = models.CharField(max_length=50, blank=True)  # e.g., "desktop-icon"

    def __str__(self):
        return self.name


class Property(models.Model):
    inventory_type = models.ForeignKey(
        InventoryType, related_name="properties", on_delete=models.CASCADE
    )
    label = models.CharField(max_length=100)
    default_value = models.CharField(
        max_length=255, blank=True, null=True
    )  # Added this
    has_name_input = models.BooleanField(default=False)
    is_required = models.BooleanField(default=False)


class Part(models.Model):
    parent_type = models.ForeignKey(
        InventoryType, related_name="parts", on_delete=models.CASCADE
    )
    part_type = models.ForeignKey(InventoryType, on_delete=models.CASCADE)
    is_default = models.BooleanField(default=True)
    has_name = models.BooleanField(default=False)  # Added this
    is_serial = models.BooleanField(default=False)  # Added this
