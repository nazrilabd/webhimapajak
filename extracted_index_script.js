  <script>
    // CSRF Token Helper
    function getCsrfToken() {
      const name = 'csrftoken';
      let cookieValue = null;
      if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
          }
        }
      }
      return cookieValue;
    }

    function addCsrfToFormData(formData) {
      const token = getCsrfToken();
      if (token) formData.append('csrfmiddlewaretoken', token);
      return formData;
    }

    // 1. Page Switcher
    function showPage(pageId) {
      document.querySelectorAll('.page-section').forEach(sec => sec.classList.remove('active'));
      const target = document.getElementById('page-' + pageId);
      if (target) {
        target.classList.add('active');
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }

      // Reset desktop top links & dropdown items
      document.querySelectorAll('.nav-link, .nav-link-top, .nav-dropdown-item').forEach(l => l.classList.remove('active'));
      const activeLink = document.getElementById('nav-' + pageId);
      if (activeLink) {
        activeLink.classList.add('active');
      }

      // Highlight parent dropdown if sub-page is active
      const dropdownParentMap = {
        'profil': 'nav-dropdown-tentang',
        'struktur': 'nav-dropdown-tentang',
        'anggota': 'nav-dropdown-tentang',
        'arsip': 'nav-dropdown-tentang',
        'berita': 'nav-dropdown-publikasi',
        'galeri': 'nav-dropdown-publikasi',
        'formulir': 'nav-dropdown-layanan',
        'aspirasi': 'nav-dropdown-layanan'
      };
      if (dropdownParentMap[pageId]) {
        const parentBtn = document.getElementById(dropdownParentMap[pageId]);
        if (parentBtn) parentBtn.classList.add('active');
      }

      // Mobile active indicator
      document.querySelectorAll('.mobile-nav-link').forEach(l => l.classList.remove('active'));
      const activeMobLink = document.getElementById('mob-nav-' + pageId);
      if (activeMobLink) {
        activeMobLink.classList.add('active');
      }

      history.pushState(null, null, '#' + pageId);

      // Re-render chart if anggaran tab is active
      if (pageId === 'anggaran') {
        renderAnggaranCharts();
      }
    }

    // 2. Mobile Menu Toggle
    const mobileBtn = document.getElementById('mobile-menu-btn');
    const mobileMenu = document.getElementById('mobile-menu');

    function toggleMobileMenu(forceClose = false) {
      if (!mobileMenu) return;
      const isHidden = mobileMenu.classList.contains('hidden');
      const icon = mobileBtn ? mobileBtn.querySelector('i') : null;

      if (forceClose || !isHidden) {
        mobileMenu.classList.add('hidden');
        if (icon) {
          icon.classList.remove('fa-xmark');
          icon.classList.add('fa-bars');
        }
      } else {
        mobileMenu.classList.remove('hidden');
        if (icon) {
          icon.classList.remove('fa-bars');
          icon.classList.add('fa-xmark');
        }
      }
    }

    if (mobileBtn) {
      mobileBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        toggleMobileMenu();
      });
    }

    // Close mobile menu on click outside or escape key
    document.addEventListener('click', (e) => {
      if (mobileMenu && !mobileMenu.classList.contains('hidden')) {
        if (!mobileMenu.contains(e.target) && !mobileBtn.contains(e.target)) {
          toggleMobileMenu(true);
        }
      }
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        toggleMobileMenu(true);
      }
    });

    // 3. Filter Data Mahasiswa (Status: all, Aktif, Alumni & Search Query)
    let currentMemberStatus = 'all';
    function setMemberFilter(status) {
      currentMemberStatus = status;
      document.querySelectorAll('.member-filter-btn').forEach(btn => {
        if (btn.getAttribute('data-filter') === status) {
          btn.className = 'member-filter-btn px-4 py-2 rounded-xl text-xs font-bold bg-brand-navy text-white shadow-sm transition';
        } else {
          btn.className = 'member-filter-btn px-4 py-2 rounded-xl text-xs font-semibold bg-slate-100 text-slate-700 hover:bg-slate-200 transition';
        }
      });
      filterMembers();
    }

    function filterMembers() {
      const query = (document.getElementById('member-search').value || '').toLowerCase().trim();
      const rows = document.querySelectorAll('.member-row');
      let visibleCount = 0;
      rows.forEach(row => {
        const name = (row.getAttribute('data-name') || '').toLowerCase();
        const nim = (row.getAttribute('data-nim') || '').toLowerCase();
        const angkatan = (row.getAttribute('data-angkatan') || '').toLowerCase();
        const divisi = (row.getAttribute('data-divisi') || '').toLowerCase();
        const status = row.getAttribute('data-status') || '';
        
        let matchStatus = false;
        if (currentMemberStatus === 'all') {
          matchStatus = true;
        } else if (currentMemberStatus === 'Aktif') {
          matchStatus = (status !== 'Alumni');
        } else if (currentMemberStatus === 'Alumni') {
          matchStatus = (status === 'Alumni');
        }

        const matchQuery = (!query || name.includes(query) || nim.includes(query) || angkatan.includes(query) || divisi.includes(query));
        if (matchStatus && matchQuery) {
          row.style.display = '';
          visibleCount++;
        } else {
          row.style.display = 'none';
        }
      });
      const countEl = document.getElementById('member-visible-count');
      if (countEl) countEl.innerText = visibleCount;
    }

    // 4. Filter Transaksi Kas (Transparansi Anggaran)
    function filterKasTable(type) {
      document.querySelectorAll('.kas-filter-btn').forEach(b => {
        if (b.innerText.toLowerCase().includes(type.toLowerCase())) {
          b.className = 'kas-filter-btn px-2.5 py-1 text-xs rounded-lg font-bold bg-brand-navy text-white';
        } else {
          b.className = 'kas-filter-btn px-2.5 py-1 text-xs rounded-lg font-medium bg-slate-100 text-slate-600';
        }
      });
      const rows = document.querySelectorAll('.kas-row');
      rows.forEach(r => {
        if (type === 'all' || r.getAttribute('data-type') === type) {
          r.style.display = '';
        } else {
          r.style.display = 'none';
        }
      });
    }

    // 5. Arsip Periode Switcher Dinamis dari Database
    const periodData = {
      {% for ar in arsip_list %}
      "{{ ar.id }}": {
        title: "Periode {{ ar.tahun_periode }}: {{ ar.nama_kabinet }}{% if ar.aktif %} (Aktif){% endif %}",
        desc: "Masa bakti {{ ar.masa_bakti|default:'-' }} • SK Rektor {{ ar.sk_rektor|default:'-' }}",
        ketua: "{{ ar.nama_ketua }}",
        nim_ketua: "{{ ar.nim_ketua|default:'' }}",
        wakil: "{{ ar.nama_wakil|default:'-' }}",
        nim_wakil: "{{ ar.nim_wakil|default:'' }}",
        sekretaris: "{{ ar.nama_sekretaris|default:'-' }}",
        bendahara: "{{ ar.nama_bendahara|default:'-' }}",
        deskripsi: "{{ ar.deskripsi|default:''|escapejs }}",
        aktif: {{ ar.aktif|yesno:"true,false" }},
        tahun: "{{ ar.tahun_periode }}",
        pengurus: [
          {% for p in ar.pengurus_list.all %}
          {
            nama: "{{ p.nama|escapejs }}",
            nim: "{{ p.nim|escapejs }}",
            jabatan: "{{ p.jabatan|escapejs }}",
            divisi: "{{ p.divisi|escapejs }}",
            bio: "{{ p.bio|escapejs }}",
            foto: "{{ p.get_foto|escapejs }}"
          },
          {% endfor %}
        ]
      },
      {% endfor %}
    };

    function changeArsipPeriod(id) {
      const p = periodData[id] || Object.values(periodData)[0];
      if (!p) return;
      document.getElementById('arsip-heading').innerText = p.title;
      document.getElementById('arsip-desc').innerText = p.desc;
      
      const badgeContainer = document.getElementById('arsip-status-badge');
      if (badgeContainer) {
        if (p.aktif) {
          badgeContainer.className = "inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-900 mb-2";
          badgeContainer.innerHTML = '<i class="fa-solid fa-circle-check"></i> Periode Aktif Berjalan';
        } else {
          badgeContainer.className = "inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-900 mb-2";
          badgeContainer.innerHTML = '<i class="fa-solid fa-landmark"></i> Arsip Demisioner Terverifikasi';
        }
      }

      // Update Pimpinan cards
      const kNama = document.getElementById('arsip-ketua-nama');
      if (kNama) kNama.innerText = p.ketua;
      const kNim = document.getElementById('arsip-ketua-nim');
      if (kNim) kNim.innerText = p.nim_ketua ? ('NIM: ' + p.nim_ketua) : '-';

      const wNama = document.getElementById('arsip-wakil-nama');
      if (wNama) wNama.innerText = p.wakil;
      const wNim = document.getElementById('arsip-wakil-nim');
      if (wNim) wNim.innerText = p.nim_wakil ? ('NIM: ' + p.nim_wakil) : '-';

      const sNama = document.getElementById('arsip-sekretaris-nama');
      if (sNama) sNama.innerText = p.sekretaris;

      const bNama = document.getElementById('arsip-bendahara-nama');
      if (bNama) bNama.innerText = p.bendahara;

      // Update Pengurus Struktur Grid
      const grid = document.getElementById('arsip-pengurus-grid');
      const countEl = document.getElementById('arsip-str-count');
      if (grid) {
        if (p.pengurus && p.pengurus.length > 0) {
          if (countEl) countEl.innerText = p.pengurus.length + ' Anggota Struktur';
          grid.innerHTML = p.pengurus.map(m => `
            <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm text-center arsip-member-card">
              <div class="w-16 h-16 rounded-xl overflow-hidden mx-auto mb-2 border border-slate-200 shadow-sm">
                <img src="${m.foto}" alt="${m.nama}" class="w-full h-full object-cover">
              </div>
              <span class="bg-brand-navy text-brand-yellow text-[9px] font-black px-2 py-0.5 rounded-full uppercase">${m.divisi}</span>
              <h4 class="font-bold text-xs text-brand-navy mt-1">${m.nama}</h4>
              <p class="text-[11px] text-slate-500 font-semibold">${m.jabatan}</p>
              <p class="text-[10px] text-slate-400 font-mono mt-0.5">${m.nim ? 'NIM: ' + m.nim : ''}</p>
              ${m.bio ? `<p class="text-[10px] text-slate-500 italic mt-1 bg-slate-50 p-1.5 rounded-lg line-clamp-2">"${m.bio}"</p>` : ''}
            </div>
          `).join('');
        } else {
          if (countEl) countEl.innerText = '0 Anggota Struktur';
          grid.innerHTML = `
            <div class="col-span-full py-6 text-center text-slate-400 text-xs">
              <i class="fa-solid fa-users-slash text-2xl mb-1 block"></i>
              Belum ada anggota struktur yang ditambahkan ke periode ini.
            </div>
          `;
        }
      }
    }

    // Trigger initial render of selected arsip period
    document.addEventListener('DOMContentLoaded', () => {
      const sel = document.getElementById('arsip-period-select');
      if (sel) changeArsipPeriod(sel.value);
    });

    function searchArsipPengurus() {
      const q = (document.getElementById('arsip-search').value || '').toLowerCase();
      const cards = document.querySelectorAll('#arsip-content-area .arsip-member-card, #arsip-content-area .p-5');
      cards.forEach(c => {
        const text = c.innerText.toLowerCase();
        c.style.display = (!q || text.includes(q)) ? '' : 'none';
      });
    }

    // 6. Modals Handler
    function openMemberDetailModal(name, job, div, nim, angkatan, email, wa, status, foto) {
      document.getElementById('md-name').innerText = name;
      document.getElementById('md-job').innerText = (job && job !== 'Anggota Divisi' && job !== 'Mahasiswa Perpajakan') ? (job + ' · ' + (div || 'Perpajakan')) : ('Program Studi Perpajakan' + (div && div !== 'Perpajakan' ? ' · ' + div : ''));
      document.getElementById('md-nim').innerText = 'NIM: ' + nim + (angkatan ? ' · Angkatan ' + angkatan : '');
      
      const prodiStatusEl = document.getElementById('md-prodi-status');
      if (prodiStatusEl) {
        prodiStatusEl.innerText = 'Program Studi Perpajakan (' + (status === 'Alumni' ? 'Alumni' : 'Mahasiswa Aktif') + ')';
      }

      // Status badge & Icon (Tanpa Foto)
      const badge = document.getElementById('md-status-badge');
      const icon = document.getElementById('md-icon');
      const isAlumni = (status === 'Alumni');
      if (isAlumni) {
        badge.className = 'text-[11px] font-bold px-3 py-0.5 rounded-full uppercase mb-1 bg-blue-100 text-blue-800 inline-flex items-center gap-1.5';
        badge.innerHTML = '<i class="fa-solid fa-graduation-cap"></i> Alumni';
        if (icon) icon.className = 'fa-solid fa-graduation-cap text-blue-600';
      } else {
        badge.className = 'text-[11px] font-bold px-3 py-0.5 rounded-full uppercase mb-1 bg-emerald-100 text-emerald-800 inline-flex items-center gap-1.5';
        badge.innerHTML = '<i class="fa-solid fa-circle-check"></i> Mahasiswa Aktif';
        if (icon) icon.className = 'fa-solid fa-user-graduate text-emerald-600';
      }

      // WhatsApp
      const waRow = document.getElementById('md-wa-row');
      const waEl = document.getElementById('md-wa');
      if (wa && wa !== 'None' && wa.trim() !== '') {
        const waClean = wa.replace(/[^0-9]/g, '');
        waEl.href = 'https://wa.me/' + waClean;
        waEl.innerText = wa;
        waRow.style.display = '';
      } else {
        waRow.style.display = 'none';
      }

      // Email
      const emailRow = document.getElementById('md-email-row');
      const emailEl = document.getElementById('md-email');
      if (email && email !== 'None' && email.trim() !== '') {
        emailEl.href = 'mailto:' + email;
        emailEl.innerText = email;
        emailRow.style.display = '';
      } else {
        emailRow.style.display = 'none';
      }

      document.getElementById('modal-member-detail').classList.remove('hidden');
    }
    function closeMemberDetailModal() {
      document.getElementById('modal-member-detail').classList.add('hidden');
    }

    function viewReceiptModal(title, amount, date, desc, imgUrl) {
      document.getElementById('rc-title').innerText = title;
      document.getElementById('rc-amount').innerText = amount;
      document.getElementById('rc-date').innerText = 'Tanggal Transaksi: ' + date;
      document.getElementById('rc-desc').innerText = desc;
      const img = document.getElementById('rc-img');
      const icon = document.getElementById('rc-icon');
      if (imgUrl) {
        img.src = imgUrl;
        img.classList.remove('hidden');
        if (icon) icon.classList.add('hidden');
      } else {
        img.classList.add('hidden');
        if (icon) icon.classList.remove('hidden');
      }
      document.getElementById('modal-receipt').classList.remove('hidden');
    }
    function closeReceiptModal() {
      document.getElementById('modal-receipt').classList.add('hidden');
    }

    function escapeHtml(str) {
      if (str === null || str === undefined) return '';
      return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
    }

    const FORMULIR_PUBLIC_DATA = {{ formulir_json_data|safe }};

    function openFormSimulation(title, formId) {
      document.getElementById('form-sim-title').innerText = title || 'Formulir Pendaftaran';

      // Fallback formId if not provided or string mismatch
      let formData = (formId && FORMULIR_PUBLIC_DATA) ? FORMULIR_PUBLIC_DATA[String(formId)] : null;
      if (!formData && FORMULIR_PUBLIC_DATA) {
        const keys = Object.keys(FORMULIR_PUBLIC_DATA);
        if (keys.length > 0) {
          if (title) {
            const titleLower = title.toLowerCase();
            for (const k of keys) {
              const item = FORMULIR_PUBLIC_DATA[k];
              if (item.judul && (titleLower.includes(item.judul.toLowerCase()) || item.judul.toLowerCase().includes(titleLower))) {
                formData = item;
                formId = item.id;
                break;
              }
            }
          }
          if (!formData) {
            formData = FORMULIR_PUBLIC_DATA[keys[0]];
            formId = formData.id;
          }
        }
      }

      const formIdEl = document.getElementById('form-sim-id');
      if (formIdEl) {
        formIdEl.value = formId || '';
      }

      // Render dynamic questions for this form (Google Form style)
      const dynamicContainer = document.getElementById('form-sim-dynamic-questions');
      if (dynamicContainer) {
        dynamicContainer.innerHTML = '';
        const questions = formData && formData.pertanyaan ? formData.pertanyaan : [];

        if (questions && questions.length > 0) {
          const header = document.createElement('div');
          header.className = 'flex items-center justify-between pb-1';
          header.innerHTML = `
            <span class="font-bold text-brand-navy text-xs flex items-center gap-1.5">
              <i class="fa-solid fa-clipboard-question text-blue-600"></i> Kuesioner / Pertanyaan Pendaftaran
            </span>
            <span class="text-[10px] text-slate-400 font-mono">${questions.length} Butir Pertanyaan</span>
          `;
          dynamicContainer.appendChild(header);

          questions.forEach((q, idx) => {
            const wrap = document.createElement('div');
            wrap.className = 'p-3 bg-slate-50 rounded-2xl border border-slate-200 space-y-1.5 text-xs';
            
            const reqStar = q.required ? '<span class="text-rose-500 font-bold">*</span>' : '<span class="text-slate-400 font-normal">(Opsional)</span>';
            const labelHtml = `<label class="block font-bold text-slate-800">${escapeHtml(q.label || ('Pertanyaan ' + (idx + 1)))} ${reqStar}</label>`;

            let inputHtml = '';
            const qName = q.id || ('q_' + idx);

            if (q.tipe === 'textarea') {
              inputHtml = `<textarea name="${qName}" rows="2" placeholder="Tuliskan jawaban Anda..." class="w-full px-3 py-2 bg-white border border-slate-200 rounded-xl text-xs focus:outline-none focus:border-brand-navy" ${q.required ? 'required' : ''}></textarea>`;
            } else if (q.tipe === 'radio') {
              const opts = (q.options || []).map((opt, oIdx) => `
                <label class="flex items-center gap-2 font-medium text-slate-700 cursor-pointer">
                  <input type="radio" name="${qName}" value="${escapeHtml(opt)}" class="text-blue-600 focus:ring-blue-500" ${oIdx === 0 && q.required ? 'required' : ''}>
                  <span>${escapeHtml(opt)}</span>
                </label>
              `).join('');
              inputHtml = `<div class="space-y-1 mt-1">${opts}</div>`;
            } else if (q.tipe === 'checkbox') {
              const opts = (q.options || []).map(opt => `
                <label class="flex items-center gap-2 font-medium text-slate-700 cursor-pointer">
                  <input type="checkbox" name="${qName}" value="${escapeHtml(opt)}" class="rounded text-blue-600 focus:ring-blue-500">
                  <span>${escapeHtml(opt)}</span>
                </label>
              `).join('');
              inputHtml = `<div class="space-y-1 mt-1">${opts}</div>`;
            } else if (q.tipe === 'select') {
              const opts = (q.options || []).map(opt => `<option value="${escapeHtml(opt)}">${escapeHtml(opt)}</option>`).join('');
              inputHtml = `
                <select name="${qName}" class="w-full px-3 py-2 bg-white border border-slate-200 rounded-xl text-xs focus:outline-none focus:border-brand-navy" ${q.required ? 'required' : ''}>
                  <option value="">-- Pilih Opsi --</option>
                  ${opts}
                </select>
              `;
            } else if (q.tipe === 'rating') {
              inputHtml = `
                <div class="flex items-center gap-3 py-1">
                  ${[1, 2, 3, 4, 5].map(val => `
                    <label class="flex flex-col items-center gap-1 cursor-pointer">
                      <input type="radio" name="${qName}" value="${val}" ${val === 5 ? 'checked' : ''} class="text-amber-500 focus:ring-amber-400">
                      <span class="text-[11px] font-bold text-slate-600">${val} ⭐</span>
                    </label>
                  `).join('')}
                </div>
              `;
            } else {
              inputHtml = `<input type="text" name="${qName}" placeholder="Jawaban singkat..." class="w-full px-3 py-2 bg-white border border-slate-200 rounded-xl text-xs focus:outline-none focus:border-brand-navy" ${q.required ? 'required' : ''}>`;
            }

            wrap.innerHTML = labelHtml + inputHtml;
            dynamicContainer.appendChild(wrap);
          });
        }
      }

      document.getElementById('modal-form-simulation').classList.remove('hidden');
    }

    function closeFormSimulation() {
      document.getElementById('modal-form-simulation').classList.add('hidden');
    }

    async function handleFormSimSubmit(e) {
      e.preventDefault();
      const form = e.target;
      const formData = new FormData(form);

      // Collect custom answers
      const customAnswers = {};
      const inputs = form.querySelectorAll('#form-sim-dynamic-questions input, #form-sim-dynamic-questions select, #form-sim-dynamic-questions textarea');
      inputs.forEach(inp => {
        if (!inp.name) return;
        if (inp.type === 'radio' && !inp.checked) return;
        if (inp.type === 'checkbox') {
          if (inp.checked) {
            if (!customAnswers[inp.name]) customAnswers[inp.name] = [];
            customAnswers[inp.name].push(inp.value);
          }
          return;
        }
        customAnswers[inp.name] = inp.value;
      });
      formData.set('jawaban_json', JSON.stringify(customAnswers));

      const btn = document.getElementById('btn-submit-form-sim');
      const origText = btn.innerHTML;
      btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> <span>Menyimpan respon ke database...</span>';
      btn.disabled = true;

      try {
        addCsrfToFormData(formData);
        const res = await fetch('/api/formulir/submit/', {
          method: 'POST',
          body: formData,
          headers: { 'X-CSRFToken': getCsrfToken() }
        });
        const data = await res.json();
        if (data.status === 'success') {
          alert('Berhasil! ' + data.message);
          closeFormSimulation();
          form.reset();
        } else {
          alert('Gagal: ' + (data.message || 'Terjadi kesalahan'));
        }
      } catch(err) {
        alert('Terjadi kesalahan jaringan atau server.');
      } finally {
        btn.innerHTML = origText;
        btn.disabled = false;
      }
    }

    function openRegisterEventModal(eventName, formId) {
      openFormSimulation('Pendaftaran: ' + eventName, formId);
    }

    function openModalNews(title, meta, content, imgUrl) {
      document.getElementById('news-modal-title').innerText = title || 'Warta Perpajakan';
      if (meta) {
        document.getElementById('news-modal-meta').innerHTML = meta;
      }
      if (content) {
        document.getElementById('news-modal-content').innerHTML = '<p class="whitespace-pre-line leading-relaxed">' + content + '</p>';
      } else {
        document.getElementById('news-modal-content').innerHTML = '<p>Informasi selengkapnya mengenai warta ini dapat dikonfirmasi langsung ke sekretariat HIMA Perpajakan UIMANDIRI.</p>';
      }
      const imgEl = document.getElementById('news-modal-img');
      if (imgUrl) {
        imgEl.src = imgUrl;
        imgEl.classList.remove('hidden');
      } else {
        imgEl.classList.add('hidden');
      }
      document.getElementById('modal-news-detail').classList.remove('hidden');
    }
    function closeModalNews() {
      document.getElementById('modal-news-detail').classList.add('hidden');
    }

    function setPublicRating(val) {
      document.getElementById('asp-rating').value = val;
      const stars = document.querySelectorAll('#stars-container .star-btn');
      stars.forEach(s => {
        const sVal = parseInt(s.getAttribute('data-val'));
        if (sVal <= val) {
          s.className = 'fa-solid fa-star star-btn';
        } else {
          s.className = 'fa-regular fa-star text-slate-300 star-btn';
        }
      });
      const labels = {
        1: '1 dari 5 (Sangat Kurang)',
        2: '2 dari 5 (Perlu Peningkatan)',
        3: '3 dari 5 (Cukup Baik)',
        4: '4 dari 5 (Puas)',
        5: '5 dari 5 (Sangat Puas)'
      };
      document.getElementById('star-rating-label').innerText = labels[val] || (val + ' dari 5');
    }

    async function handlePublicAspirasi(e) {
      e.preventDefault();
      const form = e.target;
      const formData = new FormData(form);

      const ratingVal = document.getElementById('asp-rating') ? document.getElementById('asp-rating').value : '5';
      formData.set('rating', ratingVal);

      const pengirimVal = document.getElementById('asp-pengirim') ? document.getElementById('asp-pengirim').value.trim() : '';
      formData.set('pengirim', pengirimVal || 'Mahasiswa Anonim');

      const nimVal = document.getElementById('asp-nim') ? document.getElementById('asp-nim').value.trim() : '';
      formData.set('nim', nimVal);

      // Extract custom answers from the dynamic container
      const customAnswers = {};
      let isiAspirasiText = '';
      let kategoriVal = 'Ormawa';

      const inputs = form.querySelectorAll('#asp-dynamic-questions-container input, #asp-dynamic-questions-container select, #asp-dynamic-questions-container textarea');
      inputs.forEach(inp => {
        if (!inp.name) return;
        if (inp.type === 'radio' && !inp.checked) return;
        if (inp.type === 'checkbox') {
          if (inp.checked) {
            if (!customAnswers[inp.name]) customAnswers[inp.name] = [];
            customAnswers[inp.name].push(inp.value);
          }
          return;
        }

        customAnswers[inp.name] = inp.value;
        if (inp.name === 'q_kategori') {
          kategoriVal = inp.value;
        }
        if (inp.name === 'q_isi') {
          isiAspirasiText = inp.value;
        }
      });

      if (!formData.get('kategori')) {
        formData.set('kategori', kategoriVal);
      }
      if (!formData.get('isi_aspirasi')) {
        formData.set('isi_aspirasi', isiAspirasiText || 'Aspirasi dan evaluasi kepuasan mahasiswa.');
      }
      formData.set('jawaban_json', JSON.stringify(customAnswers));

      const btn = document.getElementById('btn-submit-aspirasi-public');
      const origText = btn ? btn.innerHTML : '';
      if (btn) {
        btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Mengirim Aspirasi...';
        btn.disabled = true;
      }

      try {
        addCsrfToFormData(formData);
        const res = await fetch('/api/aspirasi/submit/', {
          method: 'POST',
          body: formData,
          headers: { 'X-CSRFToken': getCsrfToken() }
        });
        const data = await res.json();
        if (data.status === 'success') {
          alert('Terima kasih! ' + data.message);
          form.reset();
          setPublicRating(5);
        } else {
          alert('Gagal: ' + (data.message || 'Terjadi kesalahan'));
        }
      } catch(err) {
        alert('Terjadi kesalahan jaringan.');
      } finally {
        if (btn) {
          btn.innerHTML = origText;
          btn.disabled = false;
        }
      }
    }

    async function handleContactSubmit(e) {
      e.preventDefault();
      const form = e.target;
      const inputs = form.querySelectorAll('input, textarea');
      const formData = new FormData();
      formData.append('nama', inputs[0].value);
      formData.append('email', inputs[1].value);
      formData.append('subjek', inputs[2].value);
      formData.append('pesan', form.querySelector('textarea').value);

      try {
        addCsrfToFormData(formData);
        const res = await fetch('/api/kontak/submit/', {
          method: 'POST',
          body: formData,
          headers: { 'X-CSRFToken': getCsrfToken() }
        });
        const data = await res.json();
        if (data.status === 'success') {
          alert('Terima kasih! ' + data.message);
          form.reset();
        } else {
          alert('Gagal: ' + data.message);
        }
      } catch(err) {
        alert('Pesan berhasil terkirim.');
        form.reset();
      }
    }

    function downloadLPJSimulate() {
      window.open('/laporan/lpj-keuangan/', '_blank');
    }

    function openImageModal(el) {
      const img = el.querySelector('img');
      if (img) window.open(img.src, '_blank');
    }

    // 7. Render Charts Transparansi Anggaran
    let chartsRendered = false;
    function renderAnggaranCharts() {
      if (chartsRendered) return;
      chartsRendered = true;

      // Chart Arus Kas Bulanan (Bar)
      const ctxKas = document.getElementById('chartArusKasPublic');
      if (ctxKas) {
        new Chart(ctxKas, {
          type: 'bar',
          data: {
            labels: ['Sep 2026', 'Okt 2026', 'Nov 2026', 'Des 2026 (Est)', 'Jan 2027 (Est)'],
            datasets: [
              {
                label: 'Pemasukan (Rp)',
                data: [40400000, 13800000, 0, 5000000, 8000000],
                backgroundColor: '#002B5C',
                borderRadius: 6
              },
              {
                label: 'Pengeluaran (Rp)',
                data: [3450000, 6800000, 5300000, 9500000, 4000000],
                backgroundColor: '#F5C400',
                borderRadius: 6
              }
            ]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
              y: {
                beginAtZero: true,
                grid: { color: '#f1f5f9' },
                ticks: {
                  callback: val => 'Rp ' + (val/1000000) + ' Jt',
                  font: { size: 10 }
                }
              },
              x: { grid: { display: false }, ticks: { font: { size: 10 } } }
            },
            plugins: {
              legend: { position: 'bottom', labels: { boxWidth: 10, font: { size: 10 } } }
            }
          }
        });
      }

      // Chart Alokasi Belanja Pos (Doughnut)
      const ctxAlokasi = document.getElementById('chartAlokasiBelanjaPublic');
      if (ctxAlokasi) {
        new Chart(ctxAlokasi, {
          type: 'doughnut',
          data: {
            labels: ['Pelatihan Brevet (43.7%)', 'Seminar & Tax Fest (34.4%)', 'Operasional & Raker (12.2%)', 'Media & Web Server (9.7%)'],
            datasets: [{
              data: [6800000, 5300000, 3450000, 1500000],
              backgroundColor: ['#002B5C', '#F5C400', '#10B981', '#3B82F6'],
              borderWidth: 2,
              borderColor: '#ffffff'
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: { position: 'bottom', labels: { boxWidth: 10, font: { size: 10 } } }
            }
          }
        });
      }
    }

    // Initial check hash
    window.addEventListener('DOMContentLoaded', () => {
      const hash = window.location.hash.replace('#', '');
      if (hash && document.getElementById('page-' + hash)) {
        showPage(hash);
      } else {
        showPage('beranda');
      }
    });
  </script>
</body>
</html>
