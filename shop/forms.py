from django import forms
from .models import Order

# ================= SIZE CHOICES =================

SHOE_SIZES = [
    ("", "Select size"),
    ("6", "6"),
    ("7", "7"),
    ("8", "8"),
    ("9", "9"),
    ("10", "10"),
    ("11", "11"),
]

CLOTHING_SIZES = [
    ("", "Select size"),
    ("XS", "XS"),
    ("S", "S"),
    ("M", "M"),
    ("L", "L"),
    ("XL", "XL"),
    ("XXL", "XXL"),
]

PANT_SIZES = [
    ("", "Select size"),
    ("28", "28"),
    ("30", "30"),
    ("32", "32"),
    ("34", "34"),
    ("36", "36"),
]

# ================= ADD TO CART FORM =================

class AddToCartForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, initial=1)

    # default size (will change based on category in views.py)
    size = forms.ChoiceField(
        required=False,
        choices=SHOE_SIZES
    )

# ================= CHECKOUT FORM =================

class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["name", "email", "address"]