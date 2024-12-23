
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Brand
from .forms import BrandForm
from adminpanel.decorators import admin_required 



@admin_required
def create_brand(request):
    if request.method == 'POST':
        form = BrandForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('brand:brandlist')  
    else:
        form = BrandForm()
    
    return render(request, 'adminside/brand/createbrand.html', {'form': form})

def edit_brand(request, pk):
    brand = get_object_or_404(Brand, pk=pk)
    
    if request.method == 'POST':
        form = BrandForm(request.POST, instance=brand)
        if form.is_valid():
            form.save()
            messages.success(request, 'Brand updated successfully!')
            return redirect('brand:brandlist')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        # Initialize form with instance data
        form = BrandForm(instance=brand, initial={
            'brand_name': brand.brand_name,
            'description': brand.description,
            'status': brand.status
        })
    
    context = {
        'form': form,
        'brand': brand,
    }
    return render(request, 'adminside/brand/editbrand.html', context)


@admin_required
def brand_list(request):
    brands = Brand.objects.all()
    return render(request, 'adminside/brand/brandlist.html', {'brands': brands})

@admin_required
def toggle_brand(request, id):
    brand = get_object_or_404(Brand, id=id)
    brand.status = not brand.status 
    brand.save()
    return redirect('brand:brandlist')

@admin_required
def delete_brand(request, brand_id):
    if request.method == 'POST':
        brand = Brand.objects.get(id=brand_id)
        brand.delete()
        messages.success(request, f'Brand "{brand.brand_name}" was deleted successfully.')
        return redirect('brand:brandlist')
    else:
        messages.error(request, "Invalid request method.")
        return redirect('brand:brandlist')