from django.shortcuts import render, redirect,get_object_or_404
from .forms import CategoryForm
from .models import Category
from django.contrib import messages
from adminpanel.decorators import admin_required 

# Create your views here.



@admin_required
def create_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
         
            category_name = form.cleaned_data['category_name'].strip()
            
            
            if Category.objects.filter(category_name__iexact=category_name).exists():
                messages.error(request, 'A category with this name already exists.')
            else:
                form.save()  
                return redirect('category:listcategory')
    else:
        form = CategoryForm()
    return render(request, 'adminside/category/category.html', {'form': form})

@admin_required
def edit_category(request, id):
    
    category = get_object_or_404(Category, id=id)
    
    if request.method == 'POST':
        
        form = CategoryForm(request.POST, instance=category)
        
        if form.is_valid():
            
            form.save()
            return redirect('category:listcategory') 
    else:
        
        form = CategoryForm(instance=category)
    
    return render(request, 'adminside/category/editcategory.html', {'form': form, 'category': category})
@admin_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'adminside/category/listcategory.html', {'categories': categories})

@admin_required
def toggle_category_status(request, category_id):
    
    category = get_object_or_404(Category, id=category_id)

    
    category.is_active = not category.is_active
    category.save()

    if category.is_active:
        messages.success(request, f"{category.category_name} activated successfully.")
    else:
        messages.success(request, f"{category.category_name} deactivated successfully.")

    
    return redirect('category:listcategory')

@admin_required
def delete_category(request, id):
    category = Category.objects.get(id=id)
    category.delete()
    messages.success(request, f'Category "{category.category_name}" has been deleted successfully.')
    return redirect('category:listcategory')