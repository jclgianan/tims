from django import forms
from .models import InventoryItem

class InventoryForm(forms.ModelForm):
    class Meta:
        model = InventoryItem
        fields = ['inventory_id', 'category', 'item_name', 'status', 'condition']
        widgets = {
            # This adds the Bootstrap class to your Django form fields
            'item_name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.TextInput(attrs={'class': 'form-control'}),
            'inventory_id': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'condition': forms.Select(attrs={'class': 'form-select'}),
        }