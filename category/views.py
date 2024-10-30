from django.shortcuts import render, redirect,get_object_or_404
from .forms import CategoryForm
from .models import Category
from django.contrib import messages

# Create your views here.

def create_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()  
            return redirect('category:listcategory') 
    else:
        form = CategoryForm()
    return render(request, 'adminside/category/category.html', {'form': form})

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

def category_list(request):
    categories = Category.objects.all()
    return render(request, 'adminside/category/listcategory.html', {'categories': categories})


def toggle_category_status(request, category_id):
    
    category = get_object_or_404(Category, id=category_id)

    
    category.is_active = not category.is_active
    category.save()

    if category.is_active:
        messages.success(request, f"{category.category_name} activated successfully.")
    else:
        messages.success(request, f"{category.category_name} deactivated successfully.")

    
    return redirect('category:listcategory')

def delete_category(request, id):
    category = Category.objects.get(id=id)
    category.delete()
    messages.success(request, f'Category "{category.category_name}" has been deleted successfully.')
    return redirect('category:listcategory')