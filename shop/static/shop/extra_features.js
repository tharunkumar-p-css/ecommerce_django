/ extra-features.js
// Adds: client-side search, quick-view fix (extra), fake payment UI (frontend-only)

document.addEventListener('DOMContentLoaded', function () {
  /* client-side search (filters already rendered product cards) */
  (function () {
    const searchForm = document.getElementById('search-form') || document.querySelector('.search');
    if (!searchForm) return;
    const input = searchForm.querySelector('input[name="q"]') || searchForm.querySelector('input');
    if (!input) return;
    const productGrid = document.querySelector('.grid-cards') || document.querySelector('.product-grid');
    if (!productGrid) return;
    const productItems = Array.from(productGrid.children).map(el => ({ el, text: (el.textContent || '').toLowerCase() }));
    input.addEventListener('input', function (e) {
      const q = (e.target.value || '').trim().toLowerCase();
      if (!q) { productItems.forEach(p => p.el.style.display = ''); return; }
      productItems.forEach(p => p.el.style.display = p.text.indexOf(q) === -1 ? 'none' : '');
    });
  })();

  /* quick view robust attachment (if not already) */
  (function () {
    const quickButtons = document.querySelectorAll('.quick-view, .quick-view-btn');
    if (!quickButtons.length) return;
    quickButtons.forEach(btn => {
      btn.addEventListener('click', async function (ev) {
        ev.preventDefault();
        const slug = btn.dataset.slug || btn.getAttribute('data-slug');
        if (!slug) return;
        try {
          const res = await fetch(/product/${slug}/?quick=1);
          if (!res.ok) return;
          const html = await res.text();
          const quickModal = document.getElementById('quick-view');
          const quickContent = document.getElementById('quick-view-content');
          if (quickContent) {
            quickContent.innerHTML = html;
            quickModal && quickModal.classList.add('open');
            document.getElementById('page-overlay') && document.getElementById('page-overlay').classList.add('active');
          }
        } catch (err) { console.error(err); }
      });
    });
  })();

  /* fake payment injection on checkout form */
  (function () {
    const checkoutForm = document.getElementById('checkout-form') || document.querySelector('form[action$="/checkout/"]') || document.querySelector('form');
    if (!checkoutForm) return;
    if (checkoutForm.dataset.fakePaymentAttached) return;
    checkoutForm.dataset.fakePaymentAttached = '1';

    const payContainer = document.createElement('div');
    payContainer.className = 'fake-payment-container';
    payContainer.style.marginTop = '18px';
    payContainer.innerHTML = `
      <h3>Payment method</h3>
      <label style="margin-right:10px;"><input type="radio" name="payment_method" value="card" checked> Card (fake)</label>
      <label><input type="radio" name="payment_method" value="cod"> Cash on Delivery</label>
      <div id="fake-card-fields" style="margin-top:12px;">
        <label>Card number (fake)</label><br>
        <input type="text" id="fake-card-number" placeholder="4242 4242 4242 4242" style="padding:8px;border-radius:6px;border:1px solid #ddd;width:100%;max-width:320px;">
        <p style="font-size:12px;color:#666;margin-top:6px;">Use any 6+ digit number — local simulated payment only.</p>
      </div>
      <input type="hidden" name="simulate_payment" id="simulate_payment" value="0">
      <div style="margin-top:12px;"><button type="button" id="fake-pay-btn" class="btn btn-primary">Pay</button><button type="submit" id="fake-submit" style="display:none;">Place order</button></div>
      <div id="fake-payment-toast" style="display:none; position:fixed; left:50%; top:18%; transform:translateX(-50%); background:#fff; padding:14px; border-radius:8px; box-shadow:0 10px 30px rgba(0,0,0,0.12); z-index:9999;"><strong>Payment successful ✅</strong><div style="margin-top:8px;"><button id="fake-toast-ok" class="btn btn-outline">OK</button></div></div>
    `;

    checkoutForm.appendChild(payContainer);
    const cardFields = document.getElementById('fake-card-fields');
    const cardInput = document.getElementById('fake-card-number');
    const payBtn = document.getElementById('fake-pay-btn');
    const simInput = document.getElementById('simulate_payment');
    const toast = document.getElementById('fake-payment-toast');
    const toastOk = document.getElementById('fake-toast-ok');

    checkoutForm.querySelectorAll('input[name="payment_method"]').forEach(r => r.addEventListener('change', () => {
      if (checkoutForm.querySelector('input[name="payment_method"]:checked').value === 'card') cardFields.style.display = 'block';
      else cardFields.style.display = 'none';
    }));

    if (checkoutForm.querySelector('input[name="payment_method"]:checked') && checkoutForm.querySelector('input[name="payment_method"]:checked').value === 'card') cardFields.style.display = 'block';
    else cardFields.style.display = 'none';

    payBtn.addEventListener('click', function (ev) {
      ev.preventDefault();
      const method = checkoutForm.querySelector('input[name="payment_method"]:checked').value;
      if (method === 'cod') { checkoutForm.submit(); return; }
      const val = (cardInput.value || '').replace(/\s+/g, '');
      if (!val || val.length < 6) { alert('Enter a fake card number (min 6 digits) to simulate payment.'); return; }
      payBtn.disabled = true; payBtn.textContent = 'Processing...';
      setTimeout(() => { simInput.value = '1'; toast.style.display = 'block'; payBtn.disabled = false; payBtn.textContent = 'Pay'; }, 900);
    });

    toastOk && toastOk.addEventListener('click', function () { toast.style.display = 'none'; checkoutForm.submit(); });
  })();
});