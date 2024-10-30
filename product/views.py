from django.shortcuts import render, redirect
from .forms import ProductForm, ProductVariantForm
from django.shortcuts import get_object_or_404
from .models import Product ,ProductImages ,ProductVariant
from brand.models import Brand
from category.models import Category


def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.save()  
            return redirect('product:add-images', product_id=product.id) 
    else:
        form = ProductForm()
    
    return render(request, 'adminside/product/addproduct.html', {'form': form})


def add_images(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        thumbnail = request.FILES.get('thumbnail')
        images = request.FILES.getlist('images')
        
        if thumbnail:
            product.thumbnail = thumbnail
            product.save()

        for image in images:
            ProductImages.objects.create(Product=product, images=image)

        return redirect('product:list-product')

    return render(request, 'adminside/product/add_images.html', {'product': product})



def product_detail(request, product_id):
    products = get_object_or_404(Product, id=product_id) 
    images = ProductImages.objects.filter(Product=products)
    return render(request, 'adminside/product/product_detail.html', {'products': products, 'images': images})

def product_list(request):
    products = Product.objects.all()
    return render(request, 'adminside/product/product.html', {'products': products})


def toggle_product_status(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':

        product.is_active = not product.is_active
        print(product.is_active)
        product.save()
        return redirect('product:product-detail',product_id=pk)  

    return render(request, 'adminside/product/toggle_product_status.html', {'product': product})

def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    

    categories = Category.objects.all()
    brands = Brand.objects.all()

    if request.method == 'POST':

        form = ProductForm(request.POST,request.FILES,instance=product)

        if form.is_valid():

            form.save()
            return redirect('product_detail',product_id=product.id)
    else:
        form = ProductForm(instance=product)
    return render(request, 'adminside/product/editproduct.html', {
        'form': form,
        'products': product,
        'categories': categories,
        'brands': brands,
    })


def product_variant(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    variants = ProductVariant.objects.filter(Product=product)

    
    return render(request, 'adminside/variant/product_variant.html', {
        'product': product,
        'variants': variants
    })


def add_variant(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        form = ProductVariantForm(request.POST)
        if form.is_valid():
            variant = form.save(commit=False)
            variant.Product = product 
            variant.save()
            return redirect('product:product_variant', product.id) 
    else:
        form = ProductVariantForm()

    return render(request, 'adminside/variant/add_variant.html', {'form': form, 'product': product})

def edit_variant(request, variant_id):
    variant = get_object_or_404(ProductVariant, id=variant_id)

    if request.method == 'POST':
        variant.size = request.POST.get('size')
        variant.stock = request.POST.get('stock')
        variant.variant_status = request.POST.get('variant_status') == 'True'
        variant.save()

        return redirect('product:product_variant', variant.Product.id)

    return render(request, 'adminside/variant/editvariant.html', {'variant': variant})



def toggle_variant_status(request, variant_id):

    variant = get_object_or_404(ProductVariant, id=variant_id)

    variant.variant_status = not variant.variant_status
    variant.save()
    return redirect('product:product_variant', variant.Product.id)



# user side product function


def product_detail_page(request, product_id):
    product = get_object_or_404(Product, id=product_id) 
    images = ProductImages.objects.filter(Product=product)
    return render(request, 'userside/product/product.html', {'product': product, 'images': images})


