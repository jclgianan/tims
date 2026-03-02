from urllib import request

from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from .models import InventoryItem
from .forms import InventoryForm
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import InventoryType, Property, Part


def login_view(request):
    error_status = ""
    remembered_email = ""

    if request.method == "POST":
        login_input = request.POST.get("emailId")  # This is what the user typed
        password = request.POST.get("password")
        remember_me = request.POST.get("rememberMe")

        # 1. Try to find if the input is an email that belongs to a user
        try:
            user_by_email = User.objects.get(email=login_input)
            username_to_auth = user_by_email.username
        except User.DoesNotExist:
            # If no email matches, assume they typed their username
            username_to_auth = login_input

        # 2. Authenticate using the username field
        user = authenticate(request, username=username_to_auth, password=password)

        if user is not None:
            login(request, user)
            if not remember_me:
                request.session.set_expiry(0)
            return redirect("dashboard")
        else:
            error_status = "yes"
            remembered_email = login_input

    return render(
        request,
        "login.html",
        {"error": error_status, "remembered_email": remembered_email},
    )


def dashboard(request):
    return render(request, "inventory/pages/dashboard.html")


@login_required(login_url="login")
def inventory_list(request):

    items = InventoryItem.objects.all()
    all_types = InventoryType.objects.all().order_by("name")

    context = {
        "items": items,
        "all_types": all_types,  # This MUST match the template
    }
    return render(request, "inventory/pages/inventory_list.html", context)


@login_required(login_url="login")
def inventory_create(request):
    if request.method == "POST":
        # ... (your existing prefix/qty logic) ...

        # Collect dynamic properties and parts from POST
        dynamic_data = {}
        for key, value in request.POST.items():
            if key.startswith("prop_") or key.startswith("part_"):
                clean_label = (
                    key.replace("prop_", "").replace("part_", "").replace("_", " ")
                )
                dynamic_data[clean_label] = value

        # Convert dictionary to a readable string for the 'Notes' field
        spec_summary = "\n".join([f"{k}: {v}" for k, v in dynamic_data.items() if v])
        original_notes = request.POST.get("notes", "")
        final_notes = (
            f"{original_notes}\n\n--- AUTO-GENERATED SPECS ---\n{spec_summary}"
        )

        items_to_create = []
        for i in range(qty):
            # ... (ID generation logic) ...

            items_to_create.append(
                InventoryItem(
                    inventory_id=new_id,
                    item_name=request.POST.get("device_name"),
                    type_id=request.POST.get(
                        "item_type"
                    ),  # Use _id to avoid extra queries
                    status=request.POST.get("status"),
                    condition=request.POST.get("condition"),
                    # We store the dynamic stuff in notes or a dedicated JSONField
                    notes=final_notes,
                    # ... other static fields ...
                )
            )

        InventoryItem.objects.bulk_create(items_to_create)
        messages.success(request, f"Added {qty} items with dynamic specs.")
        return redirect("inventory_list")


@login_required(login_url="login")
def generate_inventory_id(request):
    type_id = request.GET.get("type_id")

    if not type_id:
        type_name = request.GET.get("category")
        inv_type = InventoryType.objects.filter(name=type_name).first()
    else:
        inv_type = InventoryType.objects.filter(id=type_id).first()

    prefix = inv_type.short_name.upper() if inv_type and inv_type.short_name else "OTH"

    # Find last inventory_id starting with the prefix
    last_item = (
        InventoryItem.objects.filter(inventory_id__startswith=f"{prefix}-")
        .order_by("-inventory_id")
        .first()
    )

    if last_item:
        # Extract last 5 digits (e.g., CS-00005 -> 5)
        try:
            last_number = int(last_item.inventory_id.split("-")[-1])
            next_number = last_number + 1
        except (ValueError, IndexError):
            next_number = 1
    else:
        next_number = 1

    # Format: PREFIX-00001
    inventory_id = f"{prefix}-{next_number:05d}"

    return JsonResponse({"inventory_id": inventory_id})


def create_inventory_type(request, type_id=None):
    all_types = InventoryType.objects.all().order_by("name")
    selected_type = None
    icon_choices = [
        ("fa-desktop", "Desktop"),
        ("fa-laptop", "Laptop"),
        ("fa-microchip", "Processor"),
        ("fa-memory", "Memory"),
        ("fa-hdd", "Hard Drive"),
        ("fa-print", "Printer"),
        ("fa-network-wired", "Network"),
    ]

    # Load existing or initialize new
    if type_id:
        selected_type = get_object_or_404(InventoryType, id=type_id)

    if request.method == "POST":
        if not selected_type:
            selected_type = InventoryType()

        name = request.POST.get("name")
        short_name = request.POST.get("short_name")
        icon = request.POST.get("icon")

        # 1. Validation: Check for duplicates ONLY if creating NEW or changing name
        duplicate_check = InventoryType.objects.filter(name__iexact=name).exclude(
            id=selected_type.id
        )
        if duplicate_check.exists():
            messages.error(request, f"Error: '{name}' already exists.")
            return redirect("inventory_type")

        # 2. Update the main object (This handles both Save and Update)
        selected_type.name = name
        selected_type.short_name = short_name
        selected_type.icon = icon
        selected_type.save()

        # 3. Sync Properties (Delete old and replace is the simplest way for dynamic rows)
        selected_type.properties.all().delete()
        labels = request.POST.getlist("prop_label[]")
        defaults = request.POST.getlist("prop_default[]")

        for i in range(len(labels)):
            if labels[i]:
                # Check if the indexed checkbox was sent in the POST data
                has_name_val = request.POST.get(f"prop_has_name_{i}") == "on"
                is_req_val = request.POST.get(f"prop_required_{i}") == "on"
                default_val = defaults[i] if i < len(defaults) else ""

                Property.objects.create(
                    inventory_type=selected_type,
                    label=labels[i],
                    default_value=default_val,
                    has_name_input=has_name_val,
                    is_required=is_req_val,
                )

        # 4. Sync Parts (handled after properties to avoid index collisions)
        selected_type.parts.all().delete()
        part_ids = request.POST.getlist("part_id[]")

        for i in range(len(part_ids)):
            if part_ids[i]:
                part_type_obj = InventoryType.objects.get(id=part_ids[i])

                # This is the "Bulletproof" way to check the checkbox
                has_name = request.POST.get(f"part_has_name_{i}") == "on"
                is_def = request.POST.get(f"part_default_{i}") == "on"
                is_ser = request.POST.get(f"part_serial_{i}") == "on"

                Part.objects.create(
                    parent_type=selected_type,
                    part_type=part_type_obj,
                    has_name=has_name,
                    is_default=is_def,
                    is_serial=is_ser,
                )

        if type_id:
            messages.success(request, f"'{name}' updated successfully!")
        else:
            messages.success(request, f"New type '{name}' created!")

        # In views.py, change the redirect slightly to ensure a fresh load
        return redirect(
            reverse("inventory_type_edit", kwargs={"type_id": selected_type.id})
        )

    context = {
        "all_types": all_types,
        "selected_type": selected_type,
        "icon_choices": icon_choices,
    }
    return render(request, "inventory/pages/inventory_type.html", context)


# views.py
def get_type_specs(request):
    type_id = request.GET.get("type_id")
    inv_type = get_object_or_404(InventoryType, id=type_id)

    # 1. Map the Properties (e.g., Processor, RAM)
    props = [
        {
            "label": p.label,
            "has_name": p.has_name_input,  # Match your model field name
            "required": p.is_required,
        }
        for p in inv_type.properties.all()
    ]

    # 2. Map the Parts (e.g., GPU, Storage)
    parts = [
        {
            "label": pt.part_type.name,
            # Check if the part itself needs a name/serial based on its own type definition
            "has_name": True,  # Or pt.part_type.short_name exists
            "required": pt.is_default,
        }
        for pt in inv_type.parts.all()
    ]

    return JsonResponse({"properties": props, "parts": parts})
