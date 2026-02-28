from django.shortcuts import redirect, render
from .models import InventoryItem
from .forms import InventoryForm
from django.http import JsonResponse
from django.contrib import messages

def inventory_list(request):

    items = InventoryItem.objects.all()
    form = InventoryForm()
    return render(request, 'inventory/pages/inventory_list.html', {'items': items, 'form': form})

def inventory_create(request):
    if request.method == "POST":
        # Get the data from the POST request
        base_id = request.POST.get('inventory_id') # e.g., "CS-00001"
        qty = int(request.POST.get('quantity', 1))
        
        # Split the ID to get the prefix and the starting number
        # Example: "CS-00001" -> prefix="CS", start_num=1
        try:
            prefix, num_str = base_id.rsplit('-', 1)
            start_num = int(num_str)
        except (ValueError, IndexError):
            messages.error(request, "Invalid Inventory ID format.")
            return redirect('inventory_list')

        # Create multiple records
        items_to_create = []
        for i in range(qty):
            current_num = start_num + i
            new_id = f"{prefix}-{current_num:05d}"
            
            # Create the object in memory (don't save to DB yet for speed)
            items_to_create.append(InventoryItem(
                inventory_id=new_id,
                item_name=request.POST.get('device_name'),
                category=request.POST.get('category'),
                status=request.POST.get('status'),
                condition=request.POST.get('condition'),
                processor=request.POST.get('processor'),
                ram=request.POST.get('ram'),
                storage=request.POST.get('storage'),
                graphics_card=request.POST.get('graphics_card'),
                issued_to=request.POST.get('issued_to'),
                office=request.POST.get('office'),
                date_acquired=request.POST.get('date_acquired') or None,
                date_issued=request.POST.get('date_issued') or None,
                notes=request.POST.get('notes')
            ))

        # Bulk save is much faster than saving one by one
        InventoryItem.objects.bulk_create(items_to_create)
        
        messages.success(request, f'Successfully added {qty} device(s) to inventory!')
        
    return redirect('inventory_list')
def generate_inventory_id(request):
    category = request.GET.get('category')
    
    # Category → prefix mapping
    prefix_map = {
        'Computer System': 'CS',
        'Components': 'CMP',
        'Peripherals': 'PER',
        'Networking': 'NET',
        'Cables & Adapters': 'CAB',
        'Others': 'OTH',
    }

    prefix = prefix_map.get(category, 'OTH')

    # Find last inventory_id starting with the prefix
    last_item = InventoryItem.objects.filter(
        inventory_id__startswith=f"{prefix}-"
    ).order_by('-inventory_id').first()

    if last_item:
        # Extract last 5 digits (e.g., CS-00005 -> 5)
        try:
            last_number = int(last_item.inventory_id.split('-')[-1])
            next_number = last_number + 1
        except (ValueError, IndexError):
            next_number = 1
    else:
        next_number = 1

    # Format: PREFIX-00001
    inventory_id = f"{prefix}-{next_number:05d}"

    return JsonResponse({'inventory_id': inventory_id})