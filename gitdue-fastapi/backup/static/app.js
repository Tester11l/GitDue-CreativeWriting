(() => {
  const $ = (s, r = document) => r.querySelector(s), $$ = (s, r = document) => [...r.querySelectorAll(s)];

  // Mobile menu
  const menu = $('.menu'), links = $('#nav-links');
  menu.addEventListener('click', () => {
    const open = menu.getAttribute('aria-expanded') !== 'true';
    menu.setAttribute('aria-expanded', open); links.classList.toggle('open', open);
  });
  $$('a', links).forEach(a => a.addEventListener('click', () => { menu.setAttribute('aria-expanded', 'false'); links.classList.remove('open'); }));

  // Tutor picker (hero mockup)
  $$('.tutor').forEach(b => b.addEventListener('click', () => {
    $$('.tutor').forEach(x => x.setAttribute('aria-pressed', 'false'));
    b.setAttribute('aria-pressed', 'true'); $('#tn').textContent = b.dataset.n;
  }));

  // FAQ accordion (one open at a time)
  $$('.faq-q').forEach(btn => btn.addEventListener('click', () => {
    const willOpen = btn.getAttribute('aria-expanded') !== 'true';
    $$('.faq-q').forEach(o => { o.setAttribute('aria-expanded', 'false'); $('#' + o.getAttribute('aria-controls')).hidden = true; });
    if (willOpen) { btn.setAttribute('aria-expanded', 'true'); $('#' + btn.getAttribute('aria-controls')).hidden = false; }
  }));

  // Pricing buttons preselect the package in the contact form
  $$('[data-plan]').forEach(a => a.addEventListener('click', () => { $('#paket').value = a.dataset.plan; }));

  // Contact form (AJAX to contact.php)
  const form = $('#f'), status = $('#status'), submit = $('button[type=submit]', form);
  form.addEventListener('submit', async e => {
    e.preventDefault();
    status.className = 'status'; status.textContent = '';
    if (!form.checkValidity()) { form.reportValidity(); return; }
    submit.disabled = true; submit.textContent = 'Mengirim...';
    try {
      const res = await fetch(form.action, { method: 'POST', body: JSON.stringify(Object.fromEntries(new FormData(form))), headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' } });
      const data = await res.json();
      if (!data.message) data.message = 'Data belum valid. Cek lagi isian formnya.';
      status.textContent = data.message; status.classList.add(data.ok ? 'ok' : 'err');
      if (data.ok) form.reset();
    } catch (err) {
      status.textContent = 'Koneksi bermasalah. Coba lagi sebentar lagi.'; status.classList.add('err');
    } finally { submit.disabled = false; submit.textContent = 'Kirim pesan'; }
  });
})();
