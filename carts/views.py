from django.shortcuts import render,redirect
from store.models import Product,Variation,VariationManager
from .models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist
# Create your views here.
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart 
def cart(request):
    return render(request,'store/cart.html')

from django.shortcuts import redirect, get_object_or_404
from .models import Cart, CartItem, Product

def add_cart(request, product_id):

    # color = request.GET['color']
    # size = request.GET['size']
    # return HttpResponse(color+' '+size)
    # exit()

    current_user = request.user
    product = get_object_or_404(Product, id=product_id)  # Get product, trả về 404 nếu không tìm thấy
    #if the user is authenticated 
    if current_user.is_authenticated:
        product_variation = []
        if request.method == "POST":
            for item in request.POST:
                key = item
                value = request.POST[key]
                # print(key,value)
                try:
                    variation = Variation.objects.get(product = product,variation_category__iexact = key,variation_value__iexact = value)
                    # print(variation)
                    product_variation.append(variation)
                except:
                    pass
        # Kiểm tra xem sản phẩm đã có trong giỏ hàng chưa
        
        is_cart_item_exists = CartItem.objects.filter(product=product, user= current_user).exists()
        if is_cart_item_exists:
                cart_item = CartItem.objects.filter(product=product, user= current_user)
             
                ex_var_list = []
                id = []
                for item in cart_item:
                    existing_variation = item.variations.all()
                    ex_var_list.append(list(existing_variation))
                    id.append(item.id)

                # print(ex_var_list)

                if product_variation in ex_var_list:
                    # increase the cart item quantity
                    index = ex_var_list.index(product_variation)
                    item_id = id[index]
                    item = CartItem.objects.get(product=product, id=item_id)
                    item.quantity += 1
                    item.save()

                else:
                    item = CartItem.objects.create(product=product, quantity=1, user = current_user)
                    if len(product_variation) > 0:
                        item.variations.clear()
                        item.variations.add(*product_variation)
                    item.save()
        else:
                cart_item = CartItem.objects.create(
                    product = product,
                    quantity = 1,
                    user = current_user,
                )
                if len(product_variation) > 0:
                    cart_item.variations.clear()
                    cart_item.variations.add(*product_variation)
                cart_item.save()
        return redirect('cart')
    #if user not authenticated
    else:
        product_variation = []
        if request.method == "POST":
            for item in request.POST:
                key = item
                value = request.POST[key]
                # print(key,value)
                try:
                    variation = Variation.objects.get(product = product,variation_category__iexact = key,variation_value__iexact = value)
                    # print(variation)
                    product_variation.append(variation)
                except:
                    pass
        
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))  # Lấy giỏ hàng hiện tại
        except Cart.DoesNotExist:
            cart = Cart.objects.create(cart_id=_cart_id(request))
        cart.save()

        
        
        # Kiểm tra xem sản phẩm đã có trong giỏ hàng chưa
        
        is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()
        if is_cart_item_exists:
                cart_item = CartItem.objects.filter(product=product, cart=cart)
                # existing_variations -> database
                # current variation -> product_variation
                # item_id -> database
                ex_var_list = []
                id = []
                for item in cart_item:
                    existing_variation = item.variations.all()
                    ex_var_list.append(list(existing_variation))
                    id.append(item.id)

                print(ex_var_list)

                if product_variation in ex_var_list:
                    # increase the cart item quantity
                    index = ex_var_list.index(product_variation)
                    item_id = id[index]
                    item = CartItem.objects.get(product=product, id=item_id)
                    item.quantity += 1
                    item.save()

                else:
                    item = CartItem.objects.create(product=product, quantity=1, cart=cart)
                    if len(product_variation) > 0:
                        item.variations.clear()
                        item.variations.add(*product_variation)
                    item.save()
        else:
                cart_item = CartItem.objects.create(
                    product = product,
                    quantity = 1,
                    cart = cart,
                )
                if len(product_variation) > 0:
                    cart_item.variations.clear()
                    cart_item.variations.add(*product_variation)
                cart_item.save()
        return redirect('cart')

def cart(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total)/100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass #just ignore

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax'       : tax,
        'grand_total': grand_total,
    }
    return render(request, 'store/cart.html', context)


def remove_cart(request, product_id,cart_item_id):
    
    product = get_object_or_404(Product, id = product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product = product,user = request.user,id = cart_item_id)
        else:
            cart = Cart.objects.get(cart_id = _cart_id(request))

            cart_item = CartItem.objects.get(product = product,cart = cart,id = cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity-=1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart') 

def remove_cart_item(request , product_id,cart_item_id): #An vo remove no remove :))

    product = get_object_or_404(Product,id = product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product = product,user = request.user,id=cart_item_id)

    else:
        cart = Cart.objects.get(cart_id = _cart_id(request))

        cart_item = CartItem.objects.get(product = product,cart = cart,id=cart_item_id)
    cart_item.delete()
    return redirect('cart')

@login_required(login_url='login')
def checkout(request,total = 0,quantity = 0,cart_items = None):
    # return render(request ,'store/checkout.html')
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        
        for cart_item in cart_items:
            total += (cart_item.product.price*cart_item.quantity)
            quantity+=cart_item.quantity

        tax = (2 * total)/100 #2% tax
        grand_total = total*tax
    except ObjectDoesNotExist:
        pass

    contenx = {
        'total':total,
        'quantity' : quantity,
        'cart_items' : cart_items,
        'tax' : tax,
        'grand_total' : grand_total,
    }
    return render(request ,'store/checkout.html',contenx)
    