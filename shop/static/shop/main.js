document.addEventListener('DOMContentLoaded', function () {
  const openCartBtn = document.getElementById('open-cart');
  const closeCartBtn = document.getElementById('close-cart');
  const cartDrawer = document.getElementById('cart-drawer');
  const overlay = document.getElementById('page-overlay');
  const quickButtons = document.querySelectorAll('.quick-view');
  const quickModal = document.getElementById('quick-view');
  const quickContent = document.getElementById('quick-view-content');

  function openCart(){cartDrawer.classList.add('open');overlay.classList.add('active');}
  function closeCart(){cartDrawer.classList.remove('open');overlay.classList.remove('active');}

  if(openCartBtn) openCartBtn.onclick=e=>{e.preventDefault();openCart();};
  if(closeCartBtn) closeCartBtn.onclick=closeCart;
  overlay.onclick=closeCart;

  quickButtons.forEach(btn=>{
    btn.addEventListener('click',async()=>{
      const slug=btn.dataset.slug;
      const res=await fetch(/product/${slug}/?quick=1);
      const html=await res.text();
      quickContent.innerHTML=html;
      quickModal.classList.add('open');
      overlay.classList.add('active');
    });
  });

  document.querySelectorAll('[data-close]').forEach(el=>{
    el.onclick=()=>{
      quickModal.classList.remove('open');
      overlay.classList.remove('active');
    };
  });
});