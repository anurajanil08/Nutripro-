from django.shortcuts import render
from product.models import Product,ProductVariant,ProductImages



# Create your views here.



def index(request):
    products = Product.objects.filter(is_active=True)
    
    product_data = []
    
    for product in products:
        variants = ProductVariant.objects.filter(Product=product)
        images = ProductImages.objects.filter(Product=product)
        
        product_data.append({
            'product': product,
            'variants': variants,
            'images': images
        })
    
    context = {
        'product_data': product_data,
    }

    return render(request, "userside/index.html", context)


def shop_page(request):
    products = Product.objects.filter(is_active=True)
    
    product_data = []
    
    for product in products:
        variants = ProductVariant.objects.filter(Product=product)
        images = ProductImages.objects.filter(Product=product)
        
        product_data.append({
            'product': product,
            'variants': variants,
            'images': images
        })
    
    context = {
        'product_data': product_data,
    }

    return render(request, "userside/store.html", context)




def about(request):
  return render(request,"about.html")