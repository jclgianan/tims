import random
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
from django.db.models import Case, When, Value
from django.db.models import Max
from django.db.models import IntegerField
from django.db.models.functions import Cast, Right


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

    items = (
        InventoryItem.objects.select_related("type", "parent")
        .prefetch_related("sub_parts", "sub_parts__type")
        .all()
        .order_by("inventory_id")
    )
    all_types = InventoryType.objects.all().order_by("name")

    context = {
        "items": items,
        "all_types": all_types,  # This MUST match the template
    }
    return render(request, "inventory/pages/inventory_list.html", context)


@login_required(login_url="login")
def inventory_create(request):
    if request.method == "POST":
        qty = int(request.POST.get("quantity", 1))
        item_type_id = request.POST.get("type")
        main_type = InventoryType.objects.get(id=item_type_id)

        # Find the highest existing number for this specific prefix to avoid duplicates
        last_item = (
            InventoryItem.objects.filter(
                inventory_id__startswith=f"{main_type.short_name}-"
            )
            .annotate(num_part=Cast(Right("inventory_id", 5), IntegerField()))
            .order_by("-num_part")
            .first()
        )

        start_number = (last_item.num_part + 1) if last_item else 1

        parents_to_create = []
        parent_ids_list = []
        current_num = start_number

        for _ in range(qty):
            # Loop to ensure the generated ID doesn't exist (double safety)
            while InventoryItem.objects.filter(
                inventory_id=f"{main_type.short_name}-{current_num:05d}"
            ).exists():
                current_num += 1

            new_id = f"{main_type.short_name}-{current_num:05d}"
            parent_ids_list.append(new_id)

            parents_to_create.append(
                InventoryItem(
                    inventory_id=new_id,
                    item_name=request.POST.get("item_name"),
                    type=main_type,
                    status=request.POST.get("status"),
                    condition=request.POST.get("condition"),
                )
            )
            current_num += 1

        # Bulk create parents to get their generated IDs back
        created_parents = InventoryItem.objects.bulk_create(parents_to_create)

        created_parents = InventoryItem.objects.filter(inventory_id__in=parent_ids_list)

        # 2. Prepare Children
        children_to_create = []

        # We fetch the list of IDs from the hidden inputs: <input type="hidden" name="part_type_id[]" value="${id}">
        submitted_part_type_ids = request.POST.getlist("part_type_id[]")

        for parent in created_parents:
            # We use a dictionary to track how many of each type we've processed
            # for THIS specific parent (to handle multiple RAM sticks, etc.)
            type_instance_count = {}

            for pt_id in submitted_part_type_ids:
                child_type = InventoryType.objects.get(id=pt_id)
                prefix = child_type.short_name.upper()

                # Update our local counter for this specific part type
                type_instance_count[pt_id] = type_instance_count.get(pt_id, 0)
                instance_index = type_instance_count[pt_id]

                # Fetch the arrays for this specific ID
                p_names = request.POST.getlist(f"part_name_{pt_id}[]")
                p_sns = request.POST.getlist(f"part_sn_{pt_id}[]")

                # Get the specific data for THIS instance of the part
                name_val = (
                    p_names[instance_index] if instance_index < len(p_names) else ""
                )
                sn_val = p_sns[instance_index] if instance_index < len(p_sns) else ""

                # ID Generation Logic (Find next available number for the prefix)
                child_num = 1
                while True:
                    potential_id = f"{prefix}-{child_num:05d}"
                    # Check DB and current unsaved batch
                    if not InventoryItem.objects.filter(
                        inventory_id=potential_id
                    ).exists() and not any(
                        c.inventory_id == potential_id for c in children_to_create
                    ):
                        child_id = potential_id
                        break
                    child_num += 1

                children_to_create.append(
                    InventoryItem(
                        inventory_id=child_id,
                        item_name=name_val
                        or f"{child_type.name} for {parent.inventory_id}",
                        type=child_type,
                        status="In Use",
                        condition=parent.condition,
                        parent=parent,
                        notes=f"S/N: {sn_val}" if sn_val else "",
                    )
                )

                # Increment so the next time we see this pt_id, we grab the next name/sn in the list
                type_instance_count[pt_id] += 1

        if children_to_create:
            InventoryItem.objects.bulk_create(children_to_create)

        messages.success(
            request, f"Successfully created {qty} devices and their components."
        )
        return redirect("inventory_list")


@login_required(login_url="login")
def generate_inventory_id(request):
    type_id = request.GET.get("type_id")
    category_name = request.GET.get("category")

    if type_id:
        inv_type = InventoryType.objects.filter(id=type_id).first()
    else:
        inv_type = InventoryType.objects.filter(name=category_name).first()

    prefix = inv_type.short_name.upper() if inv_type and inv_type.short_name else "OTH"

    # GAP-FILLER: Always finds the first unused number for this prefix
    next_number = 1
    while True:
        potential_id = f"{prefix}-{next_number:05d}"
        if not InventoryItem.objects.filter(inventory_id=potential_id).exists():
            inventory_id = potential_id
            break
        next_number += 1

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
                    is_serial=is_ser,
                    is_default=is_def,
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

    properties = [
        {
            "label": prop.label,
            "has_name": prop.has_name_input,
            "is_required": prop.is_required,
        }
        for prop in inv_type.properties.all()
    ]

    parts = []
    for pt in inv_type.parts.all():
        parts.append(
            {
                "id": pt.part_type.id,
                "label": pt.part_type.name,
                "icon": pt.part_type.icon,
                "has_name": pt.has_name,
                "is_serial": pt.is_serial,
                "is_default": pt.is_default,
            }
        )

    return JsonResponse(
        {"properties": properties, "parts": parts, "type_icon": inv_type.icon}
    )


def inventory_detail(request, inventory_id):
    item = get_object_or_404(InventoryItem, id=inventory_id)
    context = {
        "item": item,
    }
    return render(request, "inventory/pages/inventoryDetail.html", context)
