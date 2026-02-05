from decimal import Decimal
from io import BytesIO
import qrcode

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .forms import (
    AddToCartForm,
    CheckoutForm,
    SHOE_SIZES,
    CLOTHING_SIZES,
    PANT_SIZES
)
from .models import ProductComment
from django.db.models import Avg, Count




# 🔐 AUTH IMPORTS (ADD THESE)
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User
from django.contrib import messages

from .models import (
    Product,
    Category,
    CartItem,
    Order,
    OrderItem,   # ✅ ADD THIS LINE
    OfferAd
)



# ================= SESSION HELPER =================

def _get_session_key(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


# ================= HOME / PRODUCT LIST =================

def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)

    q = request.GET.get('q', '').strip()
    sort = request.GET.get('sort', '').strip()

    order_placed = request.GET.get('order') == '1'
    order_paid = request.GET.get('paid') == '1'

    # ---------- CATEGORY ----------
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    # ---------- SEARCH ----------
    if q:
        products = products.filter(
            Q(name__icontains=q) |
            Q(description__icontains=q) |
            Q(category__name__icontains=q)
        )

    # ---------- SORT ----------
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'new':
        products = products.order_by('-created_at')
    else:
        products = products.order_by('-created_at')

    # ---------- OFFER ADS (PHASE 4) ----------
    now = timezone.now()
    offer_ads = OfferAd.objects.filter(
        is_active=True,
        start_date__lte=now,
        end_date__gte=now
    ).order_by('-created_at')

    return render(request, 'shop/product_list.html', {
        'category': category,
        'categories': categories,
        'products': products,
        'offer_ads': offer_ads,
        'order_placed': order_placed,
        'order_paid': order_paid,
        'offers_page': False,
    })


# ================= OFFERS PAGE =================

def offers_list(request):
    categories = Category.objects.all()
    products = Product.objects.filter(
        available=True,
        is_on_offer=True
    )

    q = request.GET.get('q', '').strip()
    sort = request.GET.get('sort', '').strip()

    if q:
        products = products.filter(
            Q(name__icontains=q) |
            Q(description__icontains=q)
        )

    if sort == 'price_asc':
        products = products.order_by('offer_price')
    elif sort == 'price_desc':
        products = products.order_by('-offer_price')
    else:
        products = products.order_by('-created_at')

    return render(request, 'shop/product_list.html', {
        'categories': categories,
        'products': products,
        'offers_page': True,
        'category': None,
        'order_placed': False,
        'order_paid': False,
        'offer_ads': [],   # ❌ No ads on offer page
    })


# ================= PRODUCT DETAIL =================


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, available=True)

    # ================= QUICK VIEW =================
    if request.method == "GET" and request.GET.get("quick"):
        return render(request, "shop/_product_quick.html", {"product": product})

    # ================= ADD TO CART FORM =================
    form = AddToCartForm(request.POST or None)

    category = product.category.name.lower()

    if any(x in category for x in ["shoe", "sandal", "boot", "footwear"]):
        form.fields["size"].choices = SHOE_SIZES
    elif any(x in category for x in ["shirt", "tshirt", "dress"]):
        form.fields["size"].choices = CLOTHING_SIZES
    elif any(x in category for x in ["pant", "jean", "trouser"]):
        form.fields["size"].choices = PANT_SIZES
    else:
        form.fields.pop("size", None)

    # ================= HANDLE COMMENT POST =================
    if request.method == "POST" and "comment_text" in request.POST:
        if request.user.is_authenticated:
            text = request.POST.get("comment_text", "").strip()
            rating = int(request.POST.get("rating", 5))
            rating = min(max(rating, 1), 5)  # ⭐ SAFETY

            if text:
                ProductComment.objects.create(
                    product=product,
                    user=request.user,
                    text=text,
                    rating=rating
                )
        return redirect(request.path)

    # ================= HANDLE ADD TO CART =================
    if request.method == "POST" and form.is_valid():
        qty = form.cleaned_data.get("quantity", 1)
        size = form.cleaned_data.get("size")

        session_key = _get_session_key(request)

        item, created = CartItem.objects.get_or_create(
            session_key=session_key,
            product=product,
            size=size
        )

        item.quantity = qty if created else item.quantity + qty
        item.save()

        return redirect("shop:cart")

    # ================= COMMENTS QUERY =================
    comments = ProductComment.objects.filter(
        product=product
    ).order_by("-created_at")

   # ================= RATING SUMMARY =================
    rating_summary = comments.values("rating").annotate(count=Count("id"))
    total_reviews = comments.count()
    avg_rating = comments.aggregate(avg=Avg("rating"))["avg"] or 0

# Build rating_data {1:count, 2:count, ...}
    rating_data = {i: 0 for i in range(1, 6)}
    for r in rating_summary:
     rating_data[r["rating"]] = r["count"]

# Build rating_percent {1:%, 2:%, ...}
    rating_percent = {
     i: (rating_data[i] / total_reviews) * 100 if total_reviews else 0
    for i in range(1, 6)
}

# ================= AMAZON STYLE RATING ROWS =================
    rating_rows = []
    for star in range(5, 0, -1):
     rating_rows.append({
        "star": star,
        "count": rating_data[star],
        "percent": rating_percent[star],
    })

# ================= FINAL RENDER =================
    return render(request, "shop/product_detail.html", {
    "product": product,
    "form": form,
    "comments": comments,
    "rating_rows": rating_rows,
    "total_reviews": total_reviews,
    "avg_rating": round(avg_rating, 1),
    "star_range": [5, 4, 3, 2, 1],
})
# ================= CART =================

def cart_view(request):
    session_key = _get_session_key(request)
    items = CartItem.objects.filter(session_key=session_key)

    if request.method == 'POST':
        for key, value in request.POST.items():
            if key.startswith('qty_'):
                try:
                    item_id = int(key.split('_')[1])
                    qty = int(value)
                    item = CartItem.objects.get(
                        id=item_id,
                        session_key=session_key
                    )
                    if qty <= 0:
                        item.delete()
                    else:
                        item.quantity = qty
                        item.save()
                except Exception:
                    pass
        return redirect('shop:cart')

    total = sum(
        Decimal(item.product.get_display_price()) * item.quantity
        for item in items
    )

    return render(request, 'shop/cart.html', {
        'items': items,
        'total': total
    })


@require_POST
def cart_remove(request, item_id):
    session_key = _get_session_key(request)
    CartItem.objects.filter(id=item_id, session_key=session_key).delete()
    return redirect("shop:cart")



# ================= CHECKOUT =================
@login_required(login_url="shop:login")
def checkout(request):

    # Ensure session exists
    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key

    # ================= BUY NOW LOGIC =================
    buy_now_product_id = request.session.get("buy_now_product_id")

    # If user clicked Buy Now
    if buy_now_product_id:
        product = get_object_or_404(Product, id=buy_now_product_id)

        # Create a fake cart-like item list (so template works)
        items = [{
            "product": product,
            "quantity": 1,
            "size": None,
            "total_price": Decimal(str(product.get_display_price()))
        }]

        total = Decimal(str(product.get_display_price()))

    else:
        # ================= NORMAL CART LOGIC =================
        items = CartItem.objects.filter(session_key=session_key)

        if not items.exists():
            return redirect("shop:product_list")

        total = sum(
            Decimal(str(item.product.get_display_price())) * item.quantity
            for item in items
        )

    # ================= ORDER PLACE LOGIC =================
    if request.method == "POST":
        form = CheckoutForm(request.POST)

        if form.is_valid():
            order = form.save(commit=False)

            if request.user.is_authenticated:
                order.user = request.user

            method = request.POST.get("payment_method", "cod")
            order.payment_method = method

            # CARD
            if method == "card":
                order.paid = True
                order.payment_status = "COMPLETED"
                order.payment_details = "Card payment (simulated)"

            # CRYPTO
            elif method == "crypto":
                order.crypto_type = request.POST.get("crypto_type")
                order.crypto_wallet = request.POST.get("crypto_wallet")
                order.crypto_txn = request.POST.get("crypto_txn")
                order.paid = True
                order.payment_status = "COMPLETED"
                order.payment_details = "Crypto payment"

            # UPI
            elif method == "upi":
                app = request.POST.get("upi_app", "UPI")
                order.upi_app = app
                order.upi_txn = f"SIM-UPI-{app.upper()}"
                order.paid = True
                order.payment_status = "COMPLETED"
                order.payment_details = f"UPI payment via {app}"

            # COD
            else:
                order.paid = False
                order.payment_status = "PENDING"
                order.payment_details = "Cash on Delivery"

            # SAVE ORDER
            order.save()

            # ================= SAVE ORDER ITEMS =================
            # Buy now case
            if buy_now_product_id:
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=1,
                    price=product.get_display_price(),
                    size=None
                )

                # Clear buy now session after order
                request.session.pop("buy_now_product_id", None)

            # Normal cart case
            else:
                for item in items:
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        price=item.product.get_display_price(),
                        size=item.size
                    )

                # Clear cart
                items.delete()

            return redirect(
                f"{reverse('shop:product_list')}?order=1&paid={'1' if order.paid else '0'}"
            )

    return render(request, "shop/checkout.html", {
        "form": CheckoutForm(),
        "items": items,
        "total": total,
    })
# ================= UPI QR CODE =================

def upi_qr(request):
    amount = request.GET.get('amount', '0')

    payload = (
        f"upi://pay?"
        f"pa=demo@upi&"
        f"pn=FUNNELWEB&"
        f"am={amount}&"
        f"cu=INR"
    )

    qr = qrcode.make(payload)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")

    return HttpResponse(buffer.getvalue(), content_type="image/png")


# ================= API HELPERS =================

def _cart_summary_data(session_key):
    items = CartItem.objects.filter(session_key=session_key)
    count = sum(i.quantity for i in items)
    subtotal = sum(
        Decimal(i.product.get_display_price()) * i.quantity
        for i in items
    )

    html = render_to_string(
        'shop/_cart_items_fragment.html',
        {'items': items}
    )

    return {
        'count': count,
        'subtotal': subtotal,
        'itemsHtml': html
    }


def api_cart_summary(request):
    data = _cart_summary_data(request.session.session_key or '')
    return JsonResponse({
        'count': data['count'],
        'subtotal': str(data['subtotal']),
        'itemsHtml': data['itemsHtml'],
    })


@require_POST
def api_cart_add(request):
    session_key = _get_session_key(request)
    product = get_object_or_404(
        Product,
        id=request.POST.get('product_id'),
        available=True
    )
    qty = int(request.POST.get('quantity', 1))
     
    size = request.POST.get("size")

    item, created = CartItem.objects.get_or_create(
    session_key=session_key,
    product=product,
    size=size
    )

    
    item.quantity = item.quantity + qty if not created else qty
    item.save()

    return JsonResponse({
        'ok': True,
        **_cart_summary_data(session_key)
    })


def api_categories(request):
    return JsonResponse({
        "categories": [
            {
                "name": c.name,
                "url": c.get_absolute_url()
            }
            for c in Category.objects.all()
        ]
    })

def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        # 1️⃣ Check user exists
        if not User.objects.filter(username=email).exists():
            messages.error(
                request,
                "Account not found. Please register first."
            )
            return redirect("shop:register")

        # 2️⃣ Authenticate
        user = authenticate(request, username=email, password=password)

        if not user:
            messages.error(request, "Incorrect password")
            return redirect("shop:login")

        # 3️⃣ Login
        login(request, user)

        # 4️⃣ AUTO REDIRECT BASED ON ROLE
        if user.is_staff:
            return redirect("admin:index")   # Django admin
        else:
            return redirect("shop:product_list")

    return render(request, "shop/login.html")


def register_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(username=email).exists():
            messages.error(request, "User already exists")
            return redirect("shop:register")

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=request.POST.get("first_name"),
            last_name=request.POST.get("last_name"),
        )

        user.is_staff = False   # 🔒 FORCE NORMAL USER
        user.save()

        messages.success(request, "Registration successful. Please login.")
        return redirect("shop:login")

    return render(request, "shop/register.html")
def user_logout(request):
    logout(request)
    return redirect('shop:product_list')
@login_required
def user_dashboard(request):
    # safety: admin should not use user dashboard
    if request.user.is_staff:
        return redirect('admin:index')

    return render(request, 'shop/user_dashboard.html')
# ================= USER ORDERS =================

@login_required
def user_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    now = timezone.now()

    for order in orders:
        order.return_days_left = 0
        order.can_return = False

        if order.order_status == 'COMPLETED':
            deadline = order.created_at + timedelta(days=7)

            if now <= deadline:
                remaining = (deadline - now).days
                order.return_days_left = max(remaining, 1)
                order.can_return = True

    return render(request, 'shop/user_orders.html', {
        'orders': orders
    })


# ================= CANCEL ORDER =================

@login_required
def cancel_order(request, order_id):
    if request.method != "POST":
        messages.error(request, "Invalid request.")
        return redirect('shop:user_orders')

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    if order.order_status == 'PENDING':
        order.order_status = 'CANCELLED'
        order.save()
        messages.success(request, "Order cancelled successfully.")
    else:
        messages.error(request, "This order cannot be cancelled.")

    return redirect('shop:user_orders')


# ================= RETURN ORDER =================

@login_required
def return_order(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    if request.method != "POST":
        messages.error(request, "Invalid request.")
        return redirect('shop:user_orders')

    # Must be delivered
    if order.order_status != 'COMPLETED':
        messages.error(request, "This order cannot be returned.")
        return redirect('shop:user_orders')

    # ⏱️ 7-day return window
    return_deadline = order.created_at + timedelta(days=7)

    if timezone.now() > return_deadline:
        messages.error(
            request,
            "Return period expired (7 days limit)."
        )
        return redirect('shop:user_orders')

    # Prevent duplicate return
    if order.order_status == 'RETURN_REQUESTED':
        messages.warning(request, "Return already requested.")
        return redirect('shop:user_orders')

    reason = request.POST.get("reason", "").strip()

    if not reason:
        messages.error(request, "Please provide a return reason.")
        return redirect('shop:user_orders')

    order.order_status = 'RETURN_REQUESTED'
    order.return_reason = reason
    order.refund_status = 'REFUND_PENDING'
    order.save()

    messages.success(
        request,
        "Return request submitted successfully."
    )
    return redirect('shop:user_orders')

@login_required
def exchange_order(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    if request.method != "POST":
        return redirect('shop:user_orders')

    # Must be delivered
    if order.order_status != 'COMPLETED':
        messages.error(request, "Exchange allowed only for delivered orders.")
        return redirect('shop:user_orders')

    # ⏱️ 7-day exchange window
    deadline = order.created_at + timedelta(days=7)
    if timezone.now() > deadline:
        messages.error(request, "Exchange period expired (7 days).")
        return redirect('shop:user_orders')

    # Prevent duplicate exchange
    if order.order_status == 'EXCHANGE_REQUESTED':
        messages.warning(request, "Exchange already requested.")
        return redirect('shop:user_orders')

    reason = request.POST.get("reason", "").strip()
    new_product = request.POST.get("new_product", "").strip()

    if not reason or not new_product:
        messages.error(request, "All fields are required.")
        return redirect('shop:user_orders')

    order.order_status = 'EXCHANGE_REQUESTED'
    order.exchange_reason = reason
    order.exchange_product = new_product
    order.save()

    messages.success(request, "Exchange request submitted successfully.")
    return redirect('shop:user_orders')

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(
        ProductComment,
        id=comment_id,
        user=request.user   # 🔒 only owner can delete
    )
    product_slug = comment.product.slug
    comment.delete()
    return redirect("shop:product_detail", slug=product_slug)


@login_required(login_url="shop:login")
def buy_now(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Store only in session (NOT in cart table)
    request.session['buy_now_product_id'] = product.id
    request.session['buy_now_qty'] = 1

    return redirect('shop:checkout')



@require_POST
@login_required(login_url="shop:login")
def add_to_cart(request, product_id):

    session_key = _get_session_key(request)
    product = get_object_or_404(Product, id=product_id, available=True)

    item, created = CartItem.objects.get_or_create(
        session_key=session_key,
        product=product,
        size=None
    )

    if created:
        item.quantity = 1
    else:
        item.quantity += 1

    item.save()
    return redirect("shop:cart")
