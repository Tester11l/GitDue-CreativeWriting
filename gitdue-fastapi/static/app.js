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

  // Course catalog search and filters
  const courseGrid = $('#course-grid');
  if (courseGrid) {
    const cards = $$('.course-card', courseGrid);
    const filters = $$('.catalog-filter');
    const search = $('#course-search');
    const count = $('#catalog-count');
    const empty = $('#catalog-empty');
    let activeFilter = 'all';

    const updateCatalog = () => {
      const query = search.value.trim().toLocaleLowerCase();
      let visible = 0;
      cards.forEach(card => {
        const matchesFilter = activeFilter === 'all' || card.dataset.category.split(' ').includes(activeFilter);
        const matchesSearch = `${card.dataset.search} ${card.textContent}`.toLocaleLowerCase().includes(query);
        const show = matchesFilter && matchesSearch;
        card.hidden = !show;
        if (show) visible += 1;
      });
      count.textContent = `${visible} kelas ditemukan`;
      empty.hidden = visible !== 0;
    };

    filters.forEach(button => button.addEventListener('click', () => {
      activeFilter = button.dataset.filter;
      filters.forEach(filter => filter.setAttribute('aria-pressed', String(filter === button)));
      updateCatalog();
    }));
    search.addEventListener('input', updateCatalog);
    updateCatalog();

    $$('[data-course]').forEach(link => link.addEventListener('click', () => {
      const message = $('textarea[name="pesan"]');
      const interest = `Saya tertarik dengan kelas: ${link.dataset.course}. Mohon info kurikulum, jadwal, dan biaya.`;
      if (!message.value.includes(link.dataset.course)) {
        message.value = message.value.trim() ? `${message.value.trim()}\n${interest}` : interest;
      }
    }));
  }

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
