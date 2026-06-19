document.addEventListener('DOMContentLoaded', function () {
  const openCartBtn = document.getElementById('open-cart');
  const closeCartBtn = document.getElementById('close-cart');
  const cartDrawer = document.getElementById('cart-drawer');
  const overlay = document.getElementById('page-overlay');
  const quickButtons = document.querySelectorAll('.quick-view');
  const quickModal = document.getElementById('quick-view');
  const quickContent = document.getElementById('quick-view-content');

  function openCart() {
    if (!cartDrawer || !overlay) return;
    cartDrawer.classList.add('open');
    overlay.classList.add('active');
  }

  function closeLayers() {
    if (cartDrawer) cartDrawer.classList.remove('open');
    if (quickModal) quickModal.classList.remove('open');
    if (overlay) overlay.classList.remove('active');
  }

  if (openCartBtn) {
    openCartBtn.onclick = function (event) {
      event.preventDefault();
      openCart();
    };
  }

  if (closeCartBtn) closeCartBtn.onclick = closeLayers;
  if (overlay) overlay.onclick = closeLayers;

  quickButtons.forEach(function (button) {
    button.addEventListener('click', async function () {
      if (!quickModal || !quickContent || !overlay) return;

      const slug = button.dataset.slug;
      const response = await fetch(`/product/${slug}/?quick=1`);
      const html = await response.text();

      quickContent.innerHTML = html;
      quickModal.classList.add('open');
      overlay.classList.add('active');
    });
  });

  document.querySelectorAll('[data-close]').forEach(function (element) {
    element.onclick = closeLayers;
  });

  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape') {
      closeLayers();
    }
  });
});
