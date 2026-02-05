from django.contrib import admin, messages
from .models import Category, Product, CartItem, Order, OfferAd
from .models import ProductComment



# ================= CATEGORY =================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


# ================= PRODUCT =================

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "price",
        "offer_price",
        "is_on_offer",
        "available",
        "category",
        "created_at",
    )
    list_editable = ("offer_price", "is_on_offer", "available")
    list_filter = ("available", "is_on_offer", "category", "created_at")
    search_fields = ("name", "category__name")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("-created_at",)


# ================= ORDER =================

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "order_status",
        "payment_method",
        "refund_status",
        "paid",
        "created_at",
    )

    list_filter = (
        "order_status",
        "payment_method",
        "refund_status",
        "paid",
        "created_at",
    )

    search_fields = (
        "id",
        "user__username",
        "name",
        "email",
        "upi_txn",
        "crypto_txn",
    )

    readonly_fields = (
        "created_at",
        "crypto_type",
        "crypto_wallet",
        "crypto_txn",
        "upi_app",
        "upi_txn",
    )

    fieldsets = (
        ("Customer Information", {
            "fields": ("user", "name", "email", "address")
        }),
        ("Order / Return / Exchange", {
            "fields": (
                "order_status",
                "refund_status",
                "return_reason",
            )
        }),
        ("Payment Information", {
            "fields": (
                "payment_method",
                "paid",
                "payment_details",
            )
        }),
        ("UPI Details", {
            "fields": ("upi_app", "upi_txn")
        }),
        ("Crypto Details", {
            "fields": ("crypto_type", "crypto_wallet", "crypto_txn")
        }),
        ("Meta", {
            "fields": ("created_at",)
        }),
    )

    actions = (
        "mark_shipped",
        "mark_completed",
        "approve_return",
        "reject_return",
        "approve_exchange",
    )

    # ================= ACTIONS =================

    def mark_shipped(self, request, queryset):
        count = 0
        for order in queryset:
            if order.order_status == "PENDING":
                order.order_status = "SHIPPED"
                order.save()
                count += 1
        self.message_user(request, f"{count} order(s) marked as SHIPPED.", messages.SUCCESS)

    mark_shipped.short_description = "🚚 Mark as SHIPPED"


    def mark_completed(self, request, queryset):
        count = 0
        for order in queryset:
            if order.order_status == "SHIPPED":
                order.order_status = "COMPLETED"
                order.paid = True
                order.save()
                count += 1
        self.message_user(request, f"{count} order(s) marked as COMPLETED.", messages.SUCCESS)

    mark_completed.short_description = "📦 Mark as COMPLETED (Delivered)"


    def approve_return(self, request, queryset):
        count = 0
        for order in queryset:
            if order.order_status == "RETURN_REQUESTED":
                order.order_status = "RETURNED"
                order.refund_status = "REFUNDED"
                order.paid = False
                order.save()
                count += 1
        self.message_user(
            request,
            f"{count} return(s) approved and refunded.",
            messages.SUCCESS
        )

    approve_return.short_description = "✅ Approve return & refund"


    def reject_return(self, request, queryset):
        count = 0
        for order in queryset:
            if order.order_status == "RETURN_REQUESTED":
                order.order_status = "COMPLETED"
                order.refund_status = "NOT_REFUNDED"
                order.save()
                count += 1
        self.message_user(
            request,
            f"{count} return request(s) rejected.",
            messages.WARNING
        )

    reject_return.short_description = "❌ Reject return request"


    def approve_exchange(self, request, queryset):
        count = 0
        for order in queryset:
            if order.order_status == "EXCHANGE_REQUESTED":
                order.order_status = "EXCHANGED"
                # refund_status stays NOT_REFUNDED
                # paid stays True
                order.save()
                count += 1
        self.message_user(
            request,
            f"{count} exchange request(s) approved.",
            messages.SUCCESS
        )

    approve_exchange.short_description = "🔁 Approve exchange"


# ================= OFFER ADS =================

@admin.register(OfferAd)
class OfferAdAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "position",
        "is_active",
        "start_date",
        "end_date",
        "created_at",
    )
    list_filter = ("position", "is_active")
    search_fields = ("title", "subtitle")
    ordering = ("-created_at",)


# ================= CART ITEM =================

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "product",
        "size",        # 👟 ADD THIS
        "quantity",
        "session_key",
        "added_at",
    )
    list_filter = ("added_at",)
    search_fields = ("product__name", "session_key")


@admin.register(ProductComment)
class ProductCommentAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "created_at")
    search_fields = ("product_name", "user_username", "text")