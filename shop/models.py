from decimal import Decimal
from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()

# ================= CATEGORY =================

class Category(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name_plural = "Categories"

    def str(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_list_by_category', args=[self.slug])


# ================= PRODUCT =================

class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    is_on_offer = models.BooleanField(default=False)
    offer_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        ordering = ('-created_at',)

    def str(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_detail', args=[self.slug])

    def has_offer(self):
        return self.is_on_offer and self.offer_price is not None

    def get_display_price(self):
        return self.offer_price if self.has_offer() else self.price

    def discount_percent(self):
        if not self.has_offer():
            return None
        return int(((self.price - self.offer_price) / self.price) * Decimal('100'))


# ================= CART ITEM =================

class CartItem(models.Model):
    session_key = models.CharField(max_length=40)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    # 👟 Shoe size (optional)
    size = models.CharField(max_length=10, blank=True, null=True)

    added_at = models.DateTimeField(auto_now_add=True)

    # ✅ ADD THIS
    @property
    def total_price(self):
        return self.product.get_display_price() * self.quantity

    def str(self):
        return f"{self.product.name} × {self.quantity} ({self.size or 'No size'})"


# ================= ORDER =================

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    name = models.CharField(max_length=200)
    address = models.TextField()
    email = models.EmailField()

    PAYMENT_CHOICES = (
        ('cod', 'Cash on Delivery'),
        ('card', 'Card (Simulated)'),
        ('crypto', 'Cryptocurrency'),
        ('upi', 'UPI'),
    )

    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('SHIPPED', 'Shipped'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('RETURN_REQUESTED', 'Return Requested'),
        ('RETURNED', 'Returned'),
        ('REFUNDED', 'Refunded'),
        ('EXCHANGE_REQUESTED', 'Exchange Requested'),
        ('EXCHANGED', 'Exchanged'),
    )

    REFUND_CHOICES = (
        ('NOT_REFUNDED', 'Not Refunded'),
        ('REFUND_PENDING', 'Refund Pending'),
        ('REFUNDED', 'Refunded'),
    )
    PAYMENT_STATUS_CHOICES = (
    ('PENDING', 'Pending'),
    ('COMPLETED', 'Completed'),
    ('FAILED', 'Failed'),
)

    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='cod')
    order_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', db_index=True)
    payment_details = models.CharField(max_length=255, blank=True)

    return_reason = models.TextField(blank=True)
    refund_status = models.CharField(max_length=20, choices=REFUND_CHOICES, default='NOT_REFUNDED')

    exchange_reason = models.TextField(blank=True)
    exchange_product = models.CharField(max_length=255, blank=True)

    crypto_type = models.CharField(max_length=10, blank=True, null=True)
    crypto_wallet = models.CharField(max_length=255, blank=True, null=True)
    crypto_txn = models.CharField(max_length=255, blank=True, null=True)

    upi_app = models.CharField(max_length=50, blank=True, null=True)
    upi_txn = models.CharField(max_length=255, blank=True, null=True)

    paid = models.BooleanField(default=False)
    payment_status = models.CharField(
    max_length=20,
    choices=PAYMENT_STATUS_CHOICES,
    default='PENDING'
)

    def str(self):
        return f"Order #{self.id}"


# ================= ORDER ITEM =================

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    size = models.CharField(max_length=10, blank=True, null=True)  # 👟 ADD THIS

    def str(self):
        return f"{self.product.name} × {self.quantity} ({self.size or 'No size'})"


# ================= WISHLIST =================

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'session_key', 'product')

    def str(self):
        return f"Wishlist: {self.product.name}"


# ================= PRICE DROP ALERT =================

class PriceDropAlert(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    old_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_triggered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def str(self):
        return f"Price alert for {self.product.name}"


# ================= OFFER ADS =================

class OfferAd(models.Model):
    POSITION_CHOICES = (
        ('top', 'Top Banner'),
        ('card', 'Offer Card'),
        ('popup', 'Popup'),
    )

    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=255, blank=True)
    position = models.CharField(max_length=20, choices=POSITION_CHOICES)
    is_active = models.BooleanField(default=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)

    def str(self):
        return f"{self.title} ({self.position})"
    

class ProductComment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField(max_length=500)
    rating = models.PositiveIntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def str(self):
        return f"{self.user} - {self.product.name}"