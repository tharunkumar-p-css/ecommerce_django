# shop/urls.py

from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [

    # ================= HOME / PRODUCTS =================
    path('', views.product_list, name='product_list'),
    path(
        'category/<slug:category_slug>/',
        views.product_list,
        name='product_list_by_category'
    ),

    # ================= OFFERS =================
    path('offers/', views.offers_list, name='offers'),

    # ================= PRODUCT =================
    path(
        'product/<slug:slug>/',
        views.product_detail,
        name='product_detail'
    ),

    # ================= CART =================
    path('cart/', views.cart_view, name='cart'),

    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('buy-now/<int:product_id>/', views.buy_now, name='buy_now'),

    path('cart/remove/<int:item_id>/', views.cart_remove, name='cart_remove'),

    # ================= CHECKOUT =================
    path('checkout/', views.checkout, name='checkout'),

    # ================= UPI QR =================
    path('upi-qr/', views.upi_qr, name='upi_qr'),

    # ================= AUTH / USER =================
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.user_logout, name='logout'),
    path('order/<int:order_id>/return/', views.return_order, name='return_order'),
    path('order/<int:order_id>/exchange/',views.exchange_order,name='exchange_order' ),
    path("comment/delete/<int:comment_id>/", views.delete_comment, name="delete_comment"),

    # ================= USER DASHBOARD =================
    path('dashboard/', views.user_dashboard, name='dashboard'),
    path('my-orders/', views.user_orders, name='user_orders'),

    # ❌ REMOVED (not needed anymore)
    # path('my-orders/<int:order_id>/', views.order_detail, name='order_detail'),

    # ================= AJAX / API =================
    path('api/categories/', views.api_categories, name='api_categories'),
    path('api/cart/summary/', views.api_cart_summary, name='api_cart_summary'),
    path('api/cart/add/', views.api_cart_add, name='api_cart_add'),
    path('order/<int:order_id>/cancel/', views.cancel_order, name='cancel_order'),
   
   path("about/", views.about_page, name="about"),
    path("contact/", views.contact_page, name="contact"),
    path("terms/", views.terms_page, name="terms"),
]