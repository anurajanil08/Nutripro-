from django.shortcuts import render, redirect
from .forms import ProductForm, ProductVariantForm
from django.shortcuts import get_object_or_404
from .models import Product ,ProductImages ,ProductVariant
from brand.models import Brand
from category.models import Category
from django.db.models import Avg
from .models import Product, ProductImages, ProductVariant, Review
from .forms import ReviewForm
from django.contrib import messages


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


def edit_images(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product_images = ProductImages.objects.filter(Product=product)

    if request.method == 'POST':
        thumbnail = request.FILES.get('thumbnail')
        new_images = request.FILES.getlist('images')

        if thumbnail:
            product.thumbnail = thumbnail
            product.save()

        for image in new_images:
            ProductImages.objects.create(Product=product, images=image)

        image_ids_to_delete = request.POST.getlist('delete_images')
        ProductImages.objects.filter(id__in=image_ids_to_delete).delete()

        return redirect('product:product-detail', product_id=product.id)
    

    return render(request, 'adminside/product/edit_images.html', {
        'product': product,
        'product_images': product_images,
    })


def delete_image(request, image_id):
    image = get_object_or_404(ProductImages, id=image_id)
    product_id = image.Product.id
    image.delete()
    messages.success(request, "Image deleted successfully.")
    return redirect('product:edit_images', product_id=product_id)


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
        product.product_name = request.POST.get('product_name')
        product.price = request.POST.get('price')
        product.offer_price = request.POST.get('offer_price')
        product.percentage_discount = request.POST.get('percentage_discount')
        product.product_description = request.POST.get('product_description')
        product.is_active = request.POST.get('is_active') == 'True'

        category_id = request.POST.get('product_category')
        brand_id = request.POST.get('product_brand')

        if category_id:
            product.product_category = get_object_or_404(Category, id=category_id)
        if brand_id:
            product.product_brand = get_object_or_404(Brand, id=brand_id)

        product.save()
        return redirect('product:list-product')

    return render(request, 'adminside/product/editproduct.html', {
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
    variants = ProductVariant.objects.filter(Product=product, variant_status=True)
    reviews = Review.objects.filter(Product=product)  
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] 

    related_products = Product.objects.filter(
        Product_category=product.Product_category  
    ).exclude(id=product.id)[:4]

    review_form = ReviewForm()

    if request.method == 'POST':
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.user = request.user
            review.Product = product
            review.save()
            return redirect('product:product-detail-page', product_id=product.id)  

    return render(request, 'userside/product/product.html', {
        'product': product,
        'images': images,
        'variants': variants,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'review_form': review_form,
        'related_products': related_products,  
    })
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    review.delete()
    return redirect('product:product-detail-page', product_id=review.Product.id)




