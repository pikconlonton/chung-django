from django.shortcuts import render,get_object_or_404
from .models import Product
from django.http import HttpResponse
from carts.models import CartItem,Cart
from carts.views import _cart_id
from django.core.paginator import EmptyPage,PageNotAnInteger,Paginator
from django.db.models import Q
# Create your views here.

from category.models import Category
def store(request, category_slug = None):
    categories = None
    products = None
    
    if category_slug !=None:
        categories = get_object_or_404(Category,slug = category_slug)
        products = Product.objects.filter(category = categories,is_available = True)
        paginatior = Paginator(products, 2)
        page = request.GET.get('page')
        paged_products = paginatior.get_page(page)
        product_count = products.count()
    else:
        products = Product.objects.filter(is_available = True).order_by('id')
        paginatior = Paginator(products, 4)
        page = request.GET.get('page')
        paged_products = paginatior.get_page(page)

        product_count = products.count()

    context = {
        'products' : paged_products,
        'product_count' : product_count
    }

    return render(request, 'store/store.html',context)


def product_detail(request,category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id = _cart_id(request),product = single_product).exists()
        # return HttpResponse(in_cart)
        # exit

    
    except Exception as e:
        raise e
    
    context = {
        'single_product' : single_product,
        'in_cart' : in_cart,
    }
    
    return render(request ,'store/product_detail.html',context)

def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']

    if keyword:
        # Tim kiem theo discription va name cua sp
        products = Product.objects.order_by('-created_date').filter(Q(description__icontains = keyword) | Q( product_name__icontains = keyword))
        product_count = products.count()

    contex = {
        'products' : products,
        'product_count' : product_count
    }
    return render(request ,'store/store.html',contex)