// fake-payment-inject.js
// Auto-injects fake payment UI into the checkout form if present

document.addEventListener('DOMContentLoaded', function () {
  const form = document.getElementById('checkout-form') || document.querySelector('form[action$="/checkout/"], form[action$="checkout/"], form');
  if (!form) return;

  // avoid double-inject
  if (form.dataset.fakeInjected) return;
  form.dataset.fakeInjected = '1';

  const container = document.createElement('div');
  container.style.marginTop = '14px';
  container.innerHTML = `
    <h3>Payment</h3>
    <label style="margin-right:12px;"><input type="radio" name="payment_method" value="card" checked> Card (fake)</label>
    <label><input type="radio" name="payment_method" value="cod"> Cash on Delivery</label>

    <div id="fake-card-fields" style="margin-top:10px;">
      <label>Card number (fake)</label><br>
      <input id="fake-card-number" type="text" placeholder="4242 4242 4242 4242" style="padding:8px;border-radius:6px;border:1px solid #ddd;width:280px;">
      <p style="font-size:12px;color:#666;margin-top:6px;">Use any 6+ digit number. Demo only.</p>
    </div>

    <input type="hidden" name="simulate_payment" id="simulate_payment" value="0">

    <div style="margin-top:10px;">
      <button type="button" id="fake-pay-btn" class="btn btn-primary">Pay</button>
    </div>

    <div id="fake-payment-success" style="display:none;margin-top:12px;padding:10px;border-radius:8px;background:#e6ffed;border:1px solid #10b981;">
      <strong>Payment simulated ✓</strong>
      <div style="margin-top:8px;">
        <button type="button" id="fake-confirm" class="btn btn-outline">Confirm & Place Order</button>
      </div>
    </div>
  `;

  // append UI at the end of the form
  form.appendChild(container);

  const payBtn = document.getElementById('fake-pay-btn');
  const confirmBtn = document.getElementById('fake-confirm');
  const successBox = document.getElementById('fake-payment-success');
  const simInput = document.getElementById('simulate_payment');
  const cardInput = document.getElementById('fake-card-number');

  document.querySelectorAll('input[name="payment_method"]').forEach(r=>{
    r.addEventListener('change',()=>{
      if (document.querySelector('input[name="payment_method"]:checked').value === 'card')
        document.getElementById('fake-card-fields').style.display = 'block';
      else
        document.getElementById('fake-card-fields').style.display = 'none';
    });
  });

  payBtn.addEventListener('click', function (e) {
    e.preventDefault();
    const method = document.querySelector('input[name="payment_method"]:checked').value;
    if (method === 'cod') { form.submit(); return; }
    const v = (cardInput.value || '').replace(/\s+/g,'');
    if (v.length < 6) { alert('Enter a fake card number (min 6 digits).'); return; }
    payBtn.disabled = true; payBtn.innerText = 'Processing...';
    setTimeout(()=> {
      simInput.value = '1';
      successBox.style.display = 'block';
      payBtn.disabled = false; payBtn.innerText = 'Pay';
    }, 900);
  });

  confirmBtn.addEventListener('click', function() {
    form.submit();
  });
});