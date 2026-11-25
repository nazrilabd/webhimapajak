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

    // Tab Navigation
    // Tab Navigation & Page Router
    function switchTab(tabId) {
      const routes = {
        'dashboard': '/admin-dashboard/',
        'anggaran': '/admin-dashboard/anggaran/',
        'form-builder': '/admin-dashboard/formulir/',
        'formulir': '/admin-dashboard/formulir/',
        'aspirasi': '/admin-dashboard/aspirasi/',
        'anggota': '/admin-dashboard/anggota/',
        'struktur': '/admin-dashboard/struktur/',
        'arsip': '/admin-dashboard/arsip/',
        'proker': '/admin-dashboard/proker/',
        'berita': '/admin-dashboard/berita/',
        'galeri': '/admin-dashboard/galeri/',
        'profil': '/admin-dashboard/profil/',
        'multi-admin': '/admin-dashboard/pengguna/',
        'audit-log': '/admin-dashboard/audit-log/'
      };
      if (routes[tabId]) {
        window.location.href = routes[tabId];
        return;
      }
      // Fallback for single page tab switching if elements exist
      document.querySelectorAll('.admin-tab-content').forEach(c => c.classList.remove('active'));
      document.querySelectorAll('.sidebar-link').forEach(l => l.classList.remove('active'));
      const target = document.getElementById('content-' + tabId);
      const btn = document.getElementById('tab-btn-' + tabId);
      if (target) target.classList.add('active');
      if (btn) btn.classList.add('active');
    }

    // Toast Function
    let toastTimeout;
    function showToast(title, msg) {
      const toast = document.getElementById('toast-box');
      document.getElementById('toast-title').innerText = title;
      document.getElementById('toast-msg').innerText = msg;
      toast.classList.remove('translate-x-96', 'opacity-0');
      clearTimeout(toastTimeout);
      toastTimeout = setTimeout(() => {
        toast.classList.add('translate-x-96', 'opacity-0');
      }, 3500);
    }

    function toggleMobileSidebar() {
      const sidebar = document.getElementById('admin-sidebar');
      const backdrop = document.getElementById('sidebar-backdrop');
      if (!sidebar) return;
      const isClosed = sidebar.classList.contains('-translate-x-full');
      if (isClosed) {
        sidebar.classList.remove('-translate-x-full');
        if (backdrop) backdrop.classList.remove('hidden');
        document.body.classList.add('overflow-hidden');
      } else {
        sidebar.classList.add('-translate-x-full');
        if (backdrop) backdrop.classList.add('hidden');
        document.body.classList.remove('overflow-hidden');
      }
    }

    // Modal Toggles
    function openAddTransactionModal() { document.getElementById('modal-add-transaction').classList.remove('hidden'); }
    function closeAddTransactionModal() { document.getElementById('modal-add-transaction').classList.add('hidden'); }
    function openFormBuilderModal() { document.getElementById('modal-form-builder').classList.remove('hidden'); }
    function closeFormBuilderModal() { document.getElementById('modal-form-builder').classList.add('hidden'); }
    function openAddMemberModal() { document.getElementById('modal-add-member').classList.remove('hidden'); }
    function closeAddMemberModal() { document.getElementById('modal-add-member').classList.add('hidden'); }
    function openAddStrukturModal() { document.getElementById('modal-add-struktur').classList.remove('hidden'); }
    function closeAddStrukturModal() { document.getElementById('modal-add-struktur').classList.add('hidden'); }
    function openAddProkerModal() { document.getElementById('modal-add-proker').classList.remove('hidden'); }
    function closeAddProkerModal() { document.getElementById('modal-add-proker').classList.add('hidden'); }
    function closeEditProkerModal() { document.getElementById('modal-edit-proker').classList.add('hidden'); }
    function openAddBeritaModal() { document.getElementById('modal-add-berita').classList.remove('hidden'); }
    function closeAddBeritaModal() { document.getElementById('modal-add-berita').classList.add('hidden'); }
    function closeEditBeritaModal() { document.getElementById('modal-edit-berita').classList.add('hidden'); }
    function openAddGaleriModal() { document.getElementById('modal-add-galeri').classList.remove('hidden'); }
    function closeAddGaleriModal() { document.getElementById('modal-add-galeri').classList.add('hidden'); }
    function closeEditGaleriModal() { document.getElementById('modal-edit-galeri').classList.add('hidden'); }
    function openAddUserModal() { document.getElementById('modal-add-user').classList.remove('hidden'); }
    function closeAddUserModal() { document.getElementById('modal-add-user').classList.add('hidden'); }

    // ==================== AJAX ACTIONS (NEON DB & CLOUDINARY) ====================

    // 1. KAS
    async function handleTransactionSubmit(e) {
      e.preventDefault();
      const form = e.target;
      const formData = new FormData();
      formData.append('jenis', form.querySelector('input[name="trans_type"]:checked').value);
      formData.append('kategori', document.getElementById('tr-desc').value);
      formData.append('keterangan', document.getElementById('tr-desc').value);
      formData.append('nominal', document.getElementById('tr-amount').value);
      formData.append('tanggal', document.getElementById('tr-date').value);
      const fileInput = document.getElementById('tr-file');
      if (fileInput.files[0]) formData.append('bukti_transaksi', fileInput.files[0]);

      showToast('Menyimpan...', 'Mengunggah bukti ke Cloudinary dan mencatat transaksi ke database...');
      try {
        addCsrfToFormData(formData);
        const res = await fetch('/admin-api/kas/tambah/', { method: 'POST', body: formData, headers: { 'X-CSRFToken': getCsrfToken() } });
        const data = await res.json();
        if (data.status === 'success') {
          closeAddTransactionModal();
          showToast('Sukses', data.message);
          setTimeout(() => window.location.reload(), 1000);
        } else {
          showToast('Error', data.message);
        }
      } catch(err) {
        showToast('Error', 'Gagal memproses transaksi.');
      }
    }

    async function deleteKas(id) {
      if (!confirm('Yakin ingin menghapus transaksi kas ini?')) return;
      try {
        const res = await fetch('/admin-api/kas/hapus/' + id + '/', { method: 'POST', headers: { 'X-CSRFToken': getCsrfToken() } });
        const data = await res.json();
        if (data.status === 'success') {
          const row = document.getElementById('kas-row-' + id);
          if (row) row.remove();
          showToast('Dihapus', data.message);
        }
      } catch(err) {
        showToast('Error', 'Gagal menghapus transaksi.');
      }
    }

    // 2. FORM BUILDER & GOOGLE FORMS QUESTION MANAGER
    let currentQuestions = [];
    let aspirasiQuestions = [];
    let dynamicCharts = [];

    function openFormBuilderModal() {
      document.getElementById('fb-form-id').value = '';
      document.getElementById('fb-modal-title').innerText = 'Buat Formulir Online Baru';
      document.getElementById('fb-badge-mode').innerText = 'Buat Baru';
      document.getElementById('fb-badge-mode').className = 'bg-amber-100 text-amber-900 text-[10px] font-black px-2 py-0.5 rounded-full';
      document.getElementById('fb-judul').value = '';
      document.getElementById('fb-kategori').value = 'Pelatihan Brevet';
      document.getElementById('fb-deadline').value = '';
      document.getElementById('fb-kuota').value = '100';
      document.getElementById('fb-deskripsi').value = '';

      currentQuestions = [
        {
          id: 'q_' + Date.now() + '_1',
          label: 'Pilihan Minat / Bidang Divisi',
          tipe: 'radio',
          required: true,
          options: ['Pelatihan Brevet Pajak', 'Riset & Kajian Fiskal', 'Humas & Tax Center', 'Media & IT']
        },
        {
          id: 'q_' + Date.now() + '_2',
          label: 'Keahlian yang Dikuasai',
          tipe: 'checkbox',
          required: false,
          options: ['Microsoft Excel / Spreadsheet', 'Pengisian SPT Pajak', 'Desain Grafis / Canva', 'Public Speaking']
        },
        {
          id: 'q_' + Date.now() + '_3',
          label: 'Tingkat Minat Belajar Pajak (Skala 1 - 5)',
          tipe: 'rating',
          required: true,
          options: ['1', '2', '3', '4', '5']
        },
        {
          id: 'q_' + Date.now() + '_4',
          label: 'Motivasi & Alasan Mengikuti',
          tipe: 'textarea',
          required: true,
          options: []
        }
      ];
      renderQuestionsList();
      document.getElementById('modal-form-builder').classList.remove('hidden');
    }

    async function openEditFormBuilderModal(id) {
      document.getElementById('fb-form-id').value = id;
      document.getElementById('fb-modal-title').innerText = 'Edit Formulir & Atur Pertanyaan';
      document.getElementById('fb-badge-mode').innerText = 'Mode Edit (ID: ' + id + ')';
      document.getElementById('fb-badge-mode').className = 'bg-blue-100 text-blue-900 text-[10px] font-black px-2 py-0.5 rounded-full';

      try {
        const res = await fetch('/admin-api/formulir/detail/' + id + '/');
        const data = await res.json();
        if (data.status === 'success') {
          const f = data.form;
          document.getElementById('fb-judul').value = f.judul || '';
          document.getElementById('fb-kategori').value = f.kategori || 'Pelatihan Brevet';
          document.getElementById('fb-deadline').value = f.deadline || '';
          document.getElementById('fb-kuota').value = f.kuota || 100;
          document.getElementById('fb-deskripsi').value = f.deskripsi || '';
          currentQuestions = f.pertanyaan && f.pertanyaan.length > 0 ? f.pertanyaan : [];
          if (currentQuestions.length === 0) {
            currentQuestions = [
              { id: 'q_' + Date.now() + '_1', label: 'Pilihan Bidang', tipe: 'radio', required: true, options: ['Pilihan A', 'Pilihan B'] },
              { id: 'q_' + Date.now() + '_2', label: 'Catatan / Alasan', tipe: 'textarea', required: false, options: [] }
            ];
          }
          renderQuestionsList();
          document.getElementById('modal-form-builder').classList.remove('hidden');
        } else {
          showToast('Error', 'Gagal memuat detail formulir.');
        }
      } catch(e) {
        showToast('Error', 'Gagal menghubungi server.');
      }
    }

    function closeFormBuilderModal() {
      document.getElementById('modal-form-builder').classList.add('hidden');
    }

    function renderQuestionsList() {
      const container = document.getElementById('fb-questions-list');
      if (!container) return;
      container.innerHTML = '';

      if (currentQuestions.length === 0) {
        container.innerHTML = `
          <div class="text-center py-6 text-slate-400 bg-slate-50 rounded-2xl border border-dashed border-slate-200">
            <i class="fa-solid fa-list-check text-2xl text-slate-300 mb-1"></i>
            <p class="font-bold text-xs">Belum ada pertanyaan pada formulir ini.</p>
            <p class="text-[10px] text-slate-400">Klik "+ Tambah Pertanyaan" untuk menambahkan pertanyaan Google Forms.</p>
          </div>
        `;
        return;
      }

      currentQuestions.forEach((q, idx) => {
        const card = document.createElement('div');
        card.className = 'bg-white p-4 rounded-2xl border border-slate-200 shadow-sm space-y-3 relative transition hover:border-blue-400';
        
        let optionsHtml = '';
        if (['radio', 'checkbox', 'select'].includes(q.tipe)) {
          const optsList = (q.options || []).map((opt, oIdx) => `
            <div class="flex items-center gap-2">
              <span class="text-slate-400 text-xs">${q.tipe === 'radio' ? '⚪' : (q.tipe === 'checkbox' ? '☑️' : '▾')}</span>
              <input type="text" value="${escapeHtml(opt)}" onchange="updateQuestionOption(${idx}, ${oIdx}, this.value)" placeholder="Opsi ${oIdx + 1}" class="flex-1 px-2.5 py-1.5 border border-slate-200 rounded-lg text-xs">
              <button type="button" onclick="removeQuestionOption(${idx}, ${oIdx})" class="text-slate-400 hover:text-rose-600 px-1"><i class="fa-solid fa-xmark"></i></button>
            </div>
          `).join('');

          optionsHtml = `
            <div class="space-y-2 pl-2 border-l-2 border-blue-100 mt-2">
              <div class="text-[10px] font-bold text-slate-400 uppercase">Pilihan Jawaban (Opsi):</div>
              <div class="space-y-1.5">${optsList}</div>
              <button type="button" onclick="addQuestionOption(${idx})" class="text-blue-600 hover:text-blue-800 text-[11px] font-bold flex items-center gap-1 mt-1">
                <i class="fa-solid fa-plus-circle"></i> Tambah Opsi Jawaban
              </button>
            </div>
          `;
        } else if (q.tipe === 'rating') {
          optionsHtml = `
            <div class="bg-amber-50/60 p-2.5 rounded-xl border border-amber-100 text-[11px] text-amber-900 flex items-center gap-2">
              <i class="fa-solid fa-star text-amber-500"></i>
              <span>Skala Rating 1 (Sangat Rendah) sampai 5 (Sangat Tinggi / Puas).</span>
            </div>
          `;
        } else if (q.tipe === 'textarea') {
          optionsHtml = `
            <div class="bg-slate-50 p-2 rounded-xl border border-slate-100 text-[11px] text-slate-400 italic">
              Kotak teks panjang (paragraf bebas).
            </div>
          `;
        } else {
          optionsHtml = `
            <div class="bg-slate-50 p-2 rounded-xl border border-slate-100 text-[11px] text-slate-400 italic">
              Kotak teks singkat (satu baris).
            </div>
          `;
        }

        card.innerHTML = `
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 pb-2">
            <div class="flex items-center gap-2">
              <span class="w-6 h-6 rounded-full bg-blue-100 text-blue-900 font-black text-[11px] flex items-center justify-center">${idx + 1}</span>
              <span class="font-bold text-slate-700 text-xs">Pertanyaan #${idx + 1}</span>
            </div>
            <div class="flex items-center gap-2">
              <select onchange="updateQuestionType(${idx}, this.value)" class="px-2.5 py-1 border border-slate-200 rounded-lg text-xs font-semibold text-slate-700 bg-slate-50">
                <option value="text" ${q.tipe === 'text' ? 'selected' : ''}>Teks Singkat</option>
                <option value="textarea" ${q.tipe === 'textarea' ? 'selected' : ''}>Paragraf Panjang</option>
                <option value="radio" ${q.tipe === 'radio' ? 'selected' : ''}>Pilihan Ganda (Radio)</option>
                <option value="checkbox" ${q.tipe === 'checkbox' ? 'selected' : ''}>Kotak Centang (Multi-select)</option>
                <option value="select" ${q.tipe === 'select' ? 'selected' : ''}>Dropdown Pilihan</option>
                <option value="rating" ${q.tipe === 'rating' ? 'selected' : ''}>Skala Rating (1-5 ⭐)</option>
              </select>
              <button type="button" onclick="moveQuestion(${idx}, -1)" ${idx === 0 ? 'disabled' : ''} class="text-slate-400 hover:text-slate-700 disabled:opacity-30 px-1"><i class="fa-solid fa-arrow-up"></i></button>
              <button type="button" onclick="moveQuestion(${idx}, 1)" ${idx === currentQuestions.length - 1 ? 'disabled' : ''} class="text-slate-400 hover:text-slate-700 disabled:opacity-30 px-1"><i class="fa-solid fa-arrow-down"></i></button>
              <button type="button" onclick="deleteQuestionItem(${idx})" class="text-rose-500 hover:text-rose-700 px-1.5"><i class="fa-solid fa-trash-can"></i></button>
            </div>
          </div>

          <div>
            <input type="text" value="${escapeHtml(q.label || '')}" onchange="updateQuestionLabel(${idx}, this.value)" placeholder="Tuliskan pertanyaan Anda di sini..." class="w-full px-3 py-2 border border-slate-200 rounded-xl text-xs font-bold text-brand-navy focus:border-brand-navy">
          </div>

          ${optionsHtml}

          <div class="pt-2 border-t border-slate-100 flex items-center justify-between text-[11px]">
            <label class="flex items-center gap-2 cursor-pointer font-semibold text-slate-600">
              <input type="checkbox" ${q.required ? 'checked' : ''} onchange="updateQuestionRequired(${idx}, this.checked)" class="rounded text-blue-600">
              <span>Wajib diisi (Required)</span>
            </label>
            <span class="text-[10px] text-slate-400 font-mono">ID: ${q.id}</span>
          </div>
        `;
        container.appendChild(card);
      });
    }

    function addQuestionItem() {
      const newId = 'q_' + Date.now();
      currentQuestions.push({
        id: newId,
        label: '',
        tipe: 'radio',
        required: true,
        options: ['Opsi 1', 'Opsi 2']
      });
      renderQuestionsList();
    }

    function deleteQuestionItem(idx) {
      currentQuestions.splice(idx, 1);
      renderQuestionsList();
    }

    function moveQuestion(idx, dir) {
      const target = idx + dir;
      if (target < 0 || target >= currentQuestions.length) return;
      const tmp = currentQuestions[idx];
      currentQuestions[idx] = currentQuestions[target];
      currentQuestions[target] = tmp;
      renderQuestionsList();
    }

    function updateQuestionLabel(idx, val) {
      if (currentQuestions[idx]) currentQuestions[idx].label = val;
    }

    function updateQuestionType(idx, val) {
      if (currentQuestions[idx]) {
        currentQuestions[idx].tipe = val;
        if (['radio', 'checkbox', 'select'].includes(val) && (!currentQuestions[idx].options || currentQuestions[idx].options.length === 0)) {
          currentQuestions[idx].options = ['Opsi 1', 'Opsi 2'];
        } else if (val === 'rating') {
          currentQuestions[idx].options = ['1', '2', '3', '4', '5'];
        }
        renderQuestionsList();
      }
    }

    function updateQuestionRequired(idx, val) {
      if (currentQuestions[idx]) currentQuestions[idx].required = val;
    }

    function addQuestionOption(qIdx) {
      if (currentQuestions[qIdx]) {
        if (!currentQuestions[qIdx].options) currentQuestions[qIdx].options = [];
        currentQuestions[qIdx].options.push('Opsi ' + (currentQuestions[qIdx].options.length + 1));
        renderQuestionsList();
      }
    }

    function removeQuestionOption(qIdx, optIdx) {
      if (currentQuestions[qIdx] && currentQuestions[qIdx].options) {
        currentQuestions[qIdx].options.splice(optIdx, 1);
        renderQuestionsList();
      }
    }

    function updateQuestionOption(qIdx, optIdx, val) {
      if (currentQuestions[qIdx] && currentQuestions[qIdx].options) {
        currentQuestions[qIdx].options[optIdx] = val;
      }
    }

    function escapeHtml(str) {
      if (!str) return '';
      return String(str).replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/'/g, '&#39;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    }

    async function handleFormBuilderSubmit(e) {
      e.preventDefault();
      const formId = document.getElementById('fb-form-id').value;
      const judul = document.getElementById('fb-judul').value.trim();
      if (!judul) {
        showToast('Error', 'Judul formulir wajib diisi!');
        return;
      }

      const formData = new FormData();
      formData.append('judul', judul);
      formData.append('kategori', document.getElementById('fb-kategori').value);
      formData.append('deadline', document.getElementById('fb-deadline').value);
      formData.append('kuota', document.getElementById('fb-kuota').value);
      formData.append('deskripsi', document.getElementById('fb-deskripsi').value);
      formData.append('pertanyaan', JSON.stringify(currentQuestions));

      const btn = document.getElementById('btn-save-form');
      const origHtml = btn.innerHTML;
      btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Menyimpan ke Database...';
      btn.disabled = true;

      try {
        addCsrfToFormData(formData);
        const url = formId ? ('/admin-api/formulir/edit/' + formId + '/') : '/admin-api/formulir/tambah/';
        const res = await fetch(url, { method: 'POST', body: formData, headers: { 'X-CSRFToken': getCsrfToken() } });
        const data = await res.json();
        if (data.status === 'success') {
          closeFormBuilderModal();
          showToast('Sukses', data.message);
          setTimeout(() => window.location.reload(), 900);
        } else {
          showToast('Error', data.message || 'Gagal menyimpan.');
        }
      } catch(err) {
        showToast('Error', 'Gagal memproses formulir.');
      } finally {
        btn.innerHTML = origHtml;
        btn.disabled = false;
      }
    }

    async function openFormAnalyticsModal(id) {
      dynamicCharts.forEach(c => c.destroy());
      dynamicCharts = [];

      try {
        const res = await fetch('/admin-api/formulir/detail/' + id + '/');
        const data = await res.json();
        if (data.status === 'success') {
          const f = data.form;
          const a = data.analytics;
          const rList = data.responses;

          document.getElementById('fa-judul').innerText = f.judul;
          document.getElementById('fa-deskripsi').innerText = f.deskripsi || 'Formulir online aktif.';
          document.getElementById('fa-badge-kategori').innerText = f.kategori;
          document.getElementById('fa-total-respon').innerText = a.total_respon + ' Orang';
          document.getElementById('fa-kuota').innerText = a.kuota + ' Target';
          document.getElementById('fa-persen').innerText = a.persen_kuota + '%';
          document.getElementById('fa-total-pertanyaan').innerText = (f.pertanyaan || []).length + ' Butir';
          document.getElementById('fa-table-count').innerText = rList.length + ' Responden Masuk';

          const chartsContainer = document.getElementById('fa-charts-container');
          chartsContainer.innerHTML = '';

          const qStats = a.questions_analytics || [];
          if (qStats.length === 0) {
            chartsContainer.innerHTML = '<div class="col-span-2 text-center py-6 text-slate-400 bg-slate-50 rounded-2xl">Belum ada data pertanyaan untuk formulir ini.</div>';
          }

          qStats.forEach((stat, qIdx) => {
            const card = document.createElement('div');
            card.className = 'bg-white p-4 rounded-2xl border border-slate-200 shadow-sm space-y-2';

            if (['radio', 'select', 'checkbox', 'rating'].includes(stat.tipe)) {
              const canvasId = 'chart-q-' + stat.id + '-' + qIdx;
              card.innerHTML = `
                <div class="flex items-center justify-between">
                  <h5 class="font-bold text-xs text-brand-navy">${escapeHtml(stat.label)}</h5>
                  <span class="text-[9px] bg-blue-50 text-blue-800 font-bold px-2 py-0.5 rounded">${stat.tipe.toUpperCase()}</span>
                </div>
                <div class="text-[10px] text-slate-400">Total ${stat.total_answers} responden menjawab</div>
                <div class="h-48 relative"><canvas id="${canvasId}"></canvas></div>
              `;
              chartsContainer.appendChild(card);

              setTimeout(() => {
                const ctx = document.getElementById(canvasId);
                if (ctx) {
                  const labels = Object.keys(stat.counts || {});
                  const values = Object.values(stat.counts || {});
                  const palette = ['#002B5C', '#F5C400', '#10B981', '#3B82F6', '#8B5CF6', '#EC4899', '#F97316', '#64748B'];
                  
                  const chartType = (stat.tipe === 'rating' || stat.tipe === 'checkbox') ? 'bar' : 'pie';
                  const newChart = new Chart(ctx, {
                    type: chartType,
                    data: {
                      labels: labels,
                      datasets: [{
                        label: 'Jumlah Pemilih',
                        data: values,
                        backgroundColor: chartType === 'bar' ? '#002B5C' : palette.slice(0, labels.length),
                        borderRadius: 6
                      }]
                    },
                    options: {
                      responsive: true,
                      maintainAspectRatio: false,
                      plugins: {
                        legend: { position: 'bottom', labels: { boxWidth: 10, font: { size: 9 } } }
                      },
                      scales: chartType === 'bar' ? { y: { beginAtZero: true, ticks: { stepSize: 1 } }, x: { grid: { display: false } } } : {}
                    }
                  });
                  dynamicCharts.push(newChart);
                }
              }, 60);
            } else {
              const answersHtml = (stat.text_answers || []).slice(0, 5).map(item => `
                <div class="p-2 bg-slate-50 rounded-lg border border-slate-100 text-[11px]">
                  <strong class="text-brand-navy">${escapeHtml(item.nama)}:</strong>
                  <span class="text-slate-600 italic">"${escapeHtml(item.jawaban)}"</span>
                </div>
              `).join('') || '<div class="text-slate-400 text-xs italic">Belum ada jawaban teks masuk.</div>';

              card.innerHTML = `
                <div class="flex items-center justify-between">
                  <h5 class="font-bold text-xs text-brand-navy">${escapeHtml(stat.label)}</h5>
                  <span class="text-[9px] bg-slate-100 text-slate-700 font-bold px-2 py-0.5 rounded">TEKS BEBAS</span>
                </div>
                <div class="text-[10px] text-slate-400 mb-2">Total ${stat.total_answers} respon teks:</div>
                <div class="space-y-1.5 max-h-48 overflow-y-auto">${answersHtml}</div>
              `;
              chartsContainer.appendChild(card);
            }
          });

          const tbody = document.getElementById('fa-responses-tbody');
          tbody.innerHTML = '';
          if (rList.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="py-4 text-center text-slate-400">Belum ada respon masuk untuk form ini.</td></tr>';
          } else {
            rList.forEach(r => {
              const tr = document.createElement('tr');
              tr.className = 'hover:bg-slate-50';
              const jawabanJsonStr = JSON.stringify(r.jawaban || {}).replace(/"/g, '&quot;');
              tr.innerHTML = `
                <td class="py-2.5 px-3 text-slate-400">${r.created_at}</td>
                <td class="py-2.5 px-3 font-bold text-brand-navy">${escapeHtml(r.nama_lengkap)}</td>
                <td class="py-2.5 px-3 font-mono">${escapeHtml(r.nim)}</td>
                <td class="py-2.5 px-3">${escapeHtml(r.no_whatsapp)}</td>
                <td class="py-2.5 px-3 text-center">
                  <button type="button" onclick="previewJawabanLangsung('${escapeHtml(r.nama_lengkap)}', '${escapeHtml(f.judul)}', ${jawabanJsonStr})" class="px-2.5 py-1 bg-blue-50 text-blue-800 rounded font-bold hover:bg-blue-100">
                    <i class="fa-solid fa-list"></i> Lihat Respon
                  </button>
                </td>
              `;
              tbody.appendChild(tr);
            });
          }

          document.getElementById('modal-form-analytics').classList.remove('hidden');
        } else {
          showToast('Error', 'Gagal memuat analisis formulir.');
        }
      } catch(err) {
        showToast('Error', 'Gagal memuat data analitik.');
      }
    }

    function closeFormAnalyticsModal() {
      document.getElementById('modal-form-analytics').classList.add('hidden');
      dynamicCharts.forEach(c => c.destroy());
      dynamicCharts = [];
    }

    // ASPIRASI BUILDER & ANALYTICS
    async function openAspirasiBuilderModal() {
      try {
        const res = await fetch('/admin-api/aspirasi/config/');
        const data = await res.json();
        if (data.status === 'success') {
          const cfg = data.config;
          document.getElementById('ab-judul').value = cfg.judul || '';
          document.getElementById('ab-deskripsi').value = cfg.deskripsi || '';
          aspirasiQuestions = cfg.pertanyaan && cfg.pertanyaan.length > 0 ? cfg.pertanyaan : [];
          renderAspirasiQuestionsList();
          document.getElementById('modal-aspirasi-builder').classList.remove('hidden');
        }
      } catch(e) {
        showToast('Error', 'Gagal memuat konfigurasi aspirasi.');
      }
    }

    function closeAspirasiBuilderModal() {
      document.getElementById('modal-aspirasi-builder').classList.add('hidden');
    }

    function renderAspirasiQuestionsList() {
      const container = document.getElementById('ab-questions-list');
      if (!container) return;
      container.innerHTML = '';

      aspirasiQuestions.forEach((q, idx) => {
        const card = document.createElement('div');
        card.className = 'bg-white p-3.5 rounded-2xl border border-slate-200 shadow-sm space-y-2';

        let optionsHtml = '';
        if (['select', 'radio', 'checkbox'].includes(q.tipe)) {
          const opts = (q.options || []).map((o, oIdx) => `
            <div class="flex items-center gap-2">
              <input type="text" value="${escapeHtml(o)}" onchange="updateAspQuestionOption(${idx}, ${oIdx}, this.value)" class="flex-1 px-2.5 py-1 border border-slate-200 rounded-lg text-xs">
              <button type="button" onclick="removeAspQuestionOption(${idx}, ${oIdx})" class="text-rose-500 hover:text-rose-700 px-1"><i class="fa-solid fa-xmark"></i></button>
            </div>
          `).join('');

          optionsHtml = `
            <div class="space-y-1.5 pl-2 border-l-2 border-purple-200 mt-2">
              <div class="text-[10px] font-bold text-slate-400">PILIHAN OPSI:</div>
              <div class="space-y-1">${opts}</div>
              <button type="button" onclick="addAspQuestionOption(${idx})" class="text-purple-700 font-bold text-[11px] flex items-center gap-1 mt-1">
                <i class="fa-solid fa-plus-circle"></i> Tambah Opsi
              </button>
            </div>
          `;
        }

        card.innerHTML = `
          <div class="flex items-center justify-between border-b border-slate-100 pb-2">
            <span class="font-bold text-xs text-brand-navy">Pertanyaan #${idx + 1}</span>
            <div class="flex items-center gap-2">
              <select onchange="updateAspQuestionType(${idx}, this.value)" class="px-2 py-1 border border-slate-200 rounded-lg text-xs font-semibold">
                <option value="select" ${q.tipe === 'select' ? 'selected' : ''}>Dropdown Pilihan</option>
                <option value="radio" ${q.tipe === 'radio' ? 'selected' : ''}>Pilihan Ganda</option>
                <option value="checkbox" ${q.tipe === 'checkbox' ? 'selected' : ''}>Kotak Centang</option>
                <option value="rating" ${q.tipe === 'rating' ? 'selected' : ''}>Rating Skala 1-5 ⭐</option>
                <option value="textarea" ${q.tipe === 'textarea' ? 'selected' : ''}>Teks Panjang</option>
                <option value="text" ${q.tipe === 'text' ? 'selected' : ''}>Teks Singkat</option>
              </select>
              <button type="button" onclick="deleteAspQuestion(${idx})" class="text-rose-500 hover:text-rose-700 px-1"><i class="fa-solid fa-trash-can"></i></button>
            </div>
          </div>
          <div>
            <input type="text" value="${escapeHtml(q.label)}" onchange="updateAspQuestionLabel(${idx}, this.value)" placeholder="Label pertanyaan..." class="w-full px-3 py-1.5 border border-slate-200 rounded-xl text-xs font-bold text-brand-navy">
          </div>
          ${optionsHtml}
          <div class="flex items-center justify-between text-[11px] pt-1">
            <label class="flex items-center gap-2 font-semibold text-slate-600">
              <input type="checkbox" ${q.required ? 'checked' : ''} onchange="updateAspQuestionRequired(${idx}, this.checked)">
              <span>Wajib diisi</span>
            </label>
            <span class="text-[10px] text-slate-400 font-mono">ID: ${q.id}</span>
          </div>
        `;
        container.appendChild(card);
      });
    }

    function addAspirasiQuestionItem() {
      aspirasiQuestions.push({
        id: 'q_asp_' + Date.now(),
        label: 'Pertanyaan Baru',
        tipe: 'select',
        required: true,
        options: ['Opsi 1', 'Opsi 2']
      });
      renderAspirasiQuestionsList();
    }

    function deleteAspQuestion(idx) {
      aspirasiQuestions.splice(idx, 1);
      renderAspirasiQuestionsList();
    }

    function updateAspQuestionLabel(idx, val) {
      if (aspirasiQuestions[idx]) aspirasiQuestions[idx].label = val;
    }

    function updateAspQuestionType(idx, val) {
      if (aspirasiQuestions[idx]) {
        aspirasiQuestions[idx].tipe = val;
        if (['select', 'radio', 'checkbox'].includes(val) && (!aspirasiQuestions[idx].options || aspirasiQuestions[idx].options.length === 0)) {
          aspirasiQuestions[idx].options = ['Opsi 1', 'Opsi 2'];
        }
        renderAspirasiQuestionsList();
      }
    }

    function updateAspQuestionRequired(idx, val) {
      if (aspirasiQuestions[idx]) aspirasiQuestions[idx].required = val;
    }

    function addAspQuestionOption(idx) {
      if (aspirasiQuestions[idx]) {
        if (!aspirasiQuestions[idx].options) aspirasiQuestions[idx].options = [];
        aspirasiQuestions[idx].options.push('Opsi ' + (aspirasiQuestions[idx].options.length + 1));
        renderAspirasiQuestionsList();
      }
    }

    function removeAspQuestionOption(qIdx, optIdx) {
      if (aspirasiQuestions[qIdx] && aspirasiQuestions[qIdx].options) {
        aspirasiQuestions[qIdx].options.splice(optIdx, 1);
        renderAspirasiQuestionsList();
      }
    }

    function updateAspQuestionOption(qIdx, optIdx, val) {
      if (aspirasiQuestions[qIdx] && aspirasiQuestions[qIdx].options) {
        aspirasiQuestions[qIdx].options[optIdx] = val;
      }
    }

    async function handleAspirasiBuilderSubmit(e) {
      e.preventDefault();
      const formData = new FormData();
      formData.append('judul', document.getElementById('ab-judul').value.trim());
      formData.append('deskripsi', document.getElementById('ab-deskripsi').value.trim());
      formData.append('pertanyaan', JSON.stringify(aspirasiQuestions));

      try {
        addCsrfToFormData(formData);
        const res = await fetch('/admin-api/aspirasi/config/simpan/', { method: 'POST', body: formData, headers: { 'X-CSRFToken': getCsrfToken() } });
        const data = await res.json();
        if (data.status === 'success') {
          closeAspirasiBuilderModal();
          showToast('Sukses', data.message);
          setTimeout(() => window.location.reload(), 900);
        } else {
          showToast('Error', data.message);
        }
      } catch(err) {
        showToast('Error', 'Gagal menyimpan pertanyaan aspirasi.');
      }
    }

    function previewJawabanResponden(id, nama, formJudul) {
      const el = document.getElementById('data-jawaban-' + id);
      let answers = {};
      if (el) {
        try {
          answers = JSON.parse(el.textContent);
        } catch(e) {
          answers = {};
        }
      }
      previewJawabanLangsung(nama, formJudul, answers);
    }

    function previewJawabanLangsung(nama, formJudul, answers) {
      document.getElementById('dj-nama').innerText = nama;
      document.getElementById('dj-form').innerText = formJudul;
      const container = document.getElementById('dj-container');
      container.innerHTML = '';

      if (!answers || Object.keys(answers).length === 0) {
        container.innerHTML = '<div class="p-4 bg-slate-50 rounded-xl text-center text-slate-400">Tidak ada jawaban pertanyaan tambahan yang tersimpan.</div>';
      } else {
        Object.entries(answers).forEach(([k, v]) => {
          const row = document.createElement('div');
          row.className = 'p-3 bg-slate-50 rounded-xl border border-slate-100 space-y-1';
          const valDisplay = Array.isArray(v) ? v.join(', ') : (v || '-');
          row.innerHTML = `
            <div class="font-bold text-[10px] text-slate-400 uppercase tracking-wider">${escapeHtml(k)}</div>
            <div class="font-semibold text-brand-navy text-xs">${escapeHtml(valDisplay)}</div>
          `;
          container.appendChild(row);
        });
      }
      document.getElementById('modal-detail-jawaban').classList.remove('hidden');
    }

    function closeDetailJawabanModal() {
      document.getElementById('modal-detail-jawaban').classList.add('hidden');
    }

    function promptTanggapiAspirasi(id, current) {
      const resp = prompt('Masukkan tanggapan resmi pengurus HIMA untuk aspirasi ini:', current || '');
      if (resp === null) return;
      const formData = new FormData();
      formData.append('status', 'Diproses');
      formData.append('tanggapan', resp);
      formData.append('is_public', '1');
      addCsrfToFormData(formData);
      fetch('/admin-api/aspirasi/update/' + id + '/', { method: 'POST', body: formData, headers: { 'X-CSRFToken': getCsrfToken() } })
        .then(r => r.json())
        .then(data => {
          showToast('Tanggapan Dikirim', data.message);
          setTimeout(() => window.location.reload(), 800);
        });
    }

    function filterResponTable() {
      const q = (document.getElementById('search-respon-table').value || '').toLowerCase();
      const rows = document.querySelectorAll('.respon-row');
      rows.forEach(r => {
        const text = r.getAttribute('data-search') || '';
        r.style.display = text.includes(q) ? '' : 'none';
      });
    }

    async function toggleFormulir(id) {
      try {
        const res = await fetch('/admin-api/formulir/toggle/' + id + '/', { method: 'POST', headers: { 'X-CSRFToken': getCsrfToken() } });
        const data = await res.json();
        showToast('Status Form', data.message);
        setTimeout(() => window.location.reload(), 800);
      } catch(err) {
        showToast('Error', 'Gagal mengubah status formulir.');
      }
    }

    async function deleteFormulir(id) {
      if (!confirm('Hapus formulir ini beserta seluruh respon pendaftarnya?')) return;
      try {
        const res = await fetch('/admin-api/formulir/hapus/' + id + '/', { method: 'POST', headers: { 'X-CSRFToken': getCsrfToken() } });
        const data = await res.json();
        if (data.status === 'success') {
          const card = document.getElementById('form-card-' + id);
          if (card) card.remove();
          showToast('Dihapus', data.message);
        }
      } catch(err) {
        showToast('Error', 'Gagal menghapus form.');
      }
    }

    // ==================== KATEGORI GFORM CRUD ====================
    function openManageKategoriFormModal() {
      resetKategoriForm();
      document.getElementById('modal-manage-kategori-form').classList.remove('hidden');
      refreshKategoriFormList();
    }
    function closeManageKategoriFormModal() {
      document.getElementById('modal-manage-kategori-form').classList.add('hidden');
    }
    function resetKategoriForm() {
      document.getElementById('kat-form-id').value = '';
      document.getElementById('kat-form-nama').value = '';
      document.getElementById('kat-form-deskripsi').value = '';
      document.getElementById('kat-form-urutan').value = '0';
      document.getElementById('kat-form-mode-title').innerHTML = '<i class="fa-solid fa-plus-circle text-purple-600"></i> Tambah Kategori Baru';
      document.getElementById('btn-save-kat-form').innerHTML = '<i class="fa-solid fa-check"></i> Simpan Kategori';
      document.getElementById('btn-cancel-edit-kat').classList.add('hidden');
    }
    async function refreshKategoriFormList() {
      try {
        const res = await fetch('/admin-api/kategori-form/list/');
        const json = await res.json();
        if (json.status === 'success') {
          const tbody = document.getElementById('kategori-form-table-body');
          const selectFb = document.getElementById('fb-kategori');
          const currentSelected = selectFb ? selectFb.value : '';

          if (json.data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="py-4 text-center text-slate-400">Belum ada kategori formulir.</td></tr>';
          } else {
            tbody.innerHTML = json.data.map(k => `
              <tr id="kat-row-${k.id}" class="hover:bg-slate-50">
                <td class="py-2.5 px-3 font-bold text-brand-navy">${escapeHtml(k.nama)}</td>
                <td class="py-2.5 px-3 text-slate-500 max-w-xs truncate">${escapeHtml(k.deskripsi || '-')}</td>
                <td class="py-2.5 px-3 text-center font-mono text-slate-400">${k.urutan}</td>
                <td class="py-2.5 px-3 text-center font-mono font-bold text-purple-700">${k.total_formulir || 0}</td>
                <td class="py-2.5 px-3 text-center">
                  <div class="flex items-center justify-center gap-1.5">
                    <button type="button" onclick="editKategoriForm(${k.id})" class="p-1 text-blue-600 hover:bg-blue-50 rounded" title="Edit">
                      <i class="fa-solid fa-pen-to-square"></i>
                    </button>
                    <button type="button" onclick="deleteKategoriForm(${k.id})" class="p-1 text-rose-600 hover:bg-rose-50 rounded" title="Hapus">
                      <i class="fa-solid fa-trash-can"></i>
                    </button>
                  </div>
                </td>
              </tr>
            `).join('');

            if (selectFb) {
              selectFb.innerHTML = json.data.map(k => `<option value="${escapeHtml(k.nama)}" ${k.nama === currentSelected ? 'selected' : ''}>${escapeHtml(k.nama)}</option>`).join('');
            }
          }
        }
      } catch(e) {
        console.error('Error refreshing kategori form list:', e);
      }
    }
    async function handleSaveKategoriForm(e) {
      e.preventDefault();
      const id = document.getElementById('kat-form-id').value;
      const nama = document.getElementById('kat-form-nama').value.trim();
      const deskripsi = document.getElementById('kat-form-deskripsi').value.trim();
      const urutan = document.getElementById('kat-form-urutan').value;

      const formData = new FormData();
      formData.append('nama', nama);
      formData.append('deskripsi', deskripsi);
      formData.append('urutan', urutan);
      addCsrfToFormData(formData);

      const url = id ? `/admin-api/kategori-form/edit/${id}/` : '/admin-api/kategori-form/tambah/';
      showToast('Menyimpan...', 'Menyimpan kategori formulir...');
      try {
        const res = await fetch(url, { method: 'POST', body: formData, headers: { 'X-CSRFToken': getCsrfToken() } });
        const json = await res.json();
        if (json.status === 'success') {
          showToast('Sukses', json.message);
          resetKategoriForm();
          refreshKategoriFormList();
        } else {
          showToast('Error', json.message || 'Gagal menyimpan kategori.');
        }
      } catch(err) {
        showToast('Error', 'Gagal menghubungi server.');
      }
    }
    async function editKategoriForm(id) {
      try {
        const res = await fetch(`/admin-api/kategori-form/edit/${id}/`);
        const json = await res.json();
        if (json.status === 'success' && json.data) {
          const d = json.data;
          document.getElementById('kat-form-id').value = d.id;
          document.getElementById('kat-form-nama').value = d.nama || '';
          document.getElementById('kat-form-deskripsi').value = d.deskripsi || '';
          document.getElementById('kat-form-urutan').value = d.urutan || 0;
          document.getElementById('kat-form-mode-title').innerHTML = '<i class="fa-solid fa-pen-to-square text-purple-600"></i> Edit Kategori';
          document.getElementById('btn-save-kat-form').innerHTML = '<i class="fa-solid fa-check"></i> Simpan Perubahan';
          document.getElementById('btn-cancel-edit-kat').classList.remove('hidden');
          document.getElementById('kat-form-nama').focus();
        }
      } catch(err) {
        showToast('Error', 'Gagal memuat detail kategori.');
      }
    }
    async function deleteKategoriForm(id) {
      if (!confirm('Hapus kategori formulir ini?')) return;
      try {
        const res = await fetch(`/admin-api/kategori-form/hapus/${id}/`, { method: 'POST', headers: { 'X-CSRFToken': getCsrfToken() } });
        const json = await res.json();
        if (json.status === 'success') {
          showToast('Sukses', json.message);
          refreshKategoriFormList();
        } else {
          showToast('Error', json.message || 'Gagal menghapus kategori.');
        }
      } catch(err) {
        showToast('Error', 'Gagal menghubungi server.');
      }
    }

    // 3. DATA MAHASISWA & ALUMNI
    async function handleAddMemberSubmit(e) {
      e.preventDefault();
      const formData = new FormData();
      formData.append('nama', document.getElementById('mem-nama').value);
      formData.append('nim', document.getElementById('mem-nim').value);
      formData.append('angkatan', document.getElementById('mem-angkatan').value);
      formData.append('divisi', document.getElementById('mem-divisi').value);
      formData.append('jabatan', document.getElementById('mem-jabatan').value);
      formData.append('status', document.getElementById('mem-status').value);
      formData.append('no_whatsapp', document.getElementById('mem-wa').value);
      formData.append('email', document.getElementById('mem-email').value);

      const btn = document.getElementById('btn-save-member');
      btn.disabled = true;
      btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Menyimpan...';
      showToast('Menyimpan...', 'Menyimpan data mahasiswa ke database...');
      try {
        addCsrfToFormData(formData);
        const res = await fetch('/admin-api/anggota/tambah/', { method: 'POST', body: formData, headers: { 'X-CSRFToken': getCsrfToken() } });
        const data = await res.json();
        if (data.status === 'success') {
          closeAddMemberModal();
          showToast('Sukses', data.message);
          setTimeout(() => window.location.reload(), 1000);
        } else {
          showToast('Error', data.message);
          btn.disabled = false;
          btn.innerHTML = 'Simpan Mahasiswa';
        }
      } catch(err) {
        showToast('Error', 'Gagal menyimpan data mahasiswa.');
        btn.disabled = false;
        btn.innerHTML = 'Simpan Mahasiswa';
      }
    }

    async function deleteAnggota(id) {
      if (!confirm('Hapus data mahasiswa ini dari database?')) return;
      try {
        const res = await fetch('/admin-api/anggota/hapus/' + id + '/', { method: 'POST', headers: { 'X-CSRFToken': getCsrfToken() } });
        const data = await res.json();
        if (data.status === 'success') {
          const row = document.getElementById('anggota-row-' + id);
          if (row) row.remove();
          showToast('Dihapus', data.message);
        }
      } catch(err) {
        showToast('Error', 'Gagal menghapus data mahasiswa.');
      }
    }

    function openEditAnggotaModal(id, nama, nim, angkatan, divisi, jabatan, wa, email, status) {
      document.getElementById('edit-mem-id').value = id;
      document.getElementById('edit-mem-nama').value = nama;
      document.getElementById('edit-mem-nim').value = nim;
      document.getElementById('edit-mem-angkatan').value = angkatan;
      document.getElementById('edit-mem-divisi').value = divisi;
      document.getElementById('edit-mem-jabatan').value = jabatan;
      document.getElementById('edit-mem-wa').value = (wa && wa !== 'None') ? wa : '';
      document.getElementById('edit-mem-email').value = (email && email !== 'None') ? email : '';
      document.getElementById('edit-mem-status').value = status || 'Aktif';
      document.getElementById('modal-edit-member').classList.remove('hidden');
    }

    function closeEditAnggotaModal() {
      document.getElementById('modal-edit-member').classList.add('hidden');
    }

    async function handleEditMemberSubmit(e) {
      e.preventDefault();
      const id = document.getElementById('edit-mem-id').value;
      const formData = new FormData();
      formData.append('nama', document.getElementById('edit-mem-nama').value);
      formData.append('nim', document.getElementById('edit-mem-nim').value);
      formData.append('angkatan', document.getElementById('edit-mem-angkatan').value);
      formData.append('divisi', document.getElementById('edit-mem-divisi').value);
      formData.append('jabatan', document.getElementById('edit-mem-jabatan').value);
      formData.append('status', document.getElementById('edit-mem-status').value);
      formData.append('no_whatsapp', document.getElementById('edit-mem-wa').value);
      formData.append('email', document.getElementById('edit-mem-email').value);

      const btn = document.getElementById('btn-update-member');
      btn.disabled = true;
      btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Menyimpan...';
      showToast('Menyimpan...', 'Memperbarui data mahasiswa di database...');
      try {
        addCsrfToFormData(formData);
        const res = await fetch('/admin-api/anggota/edit/' + id + '/', { method: 'POST', body: formData, headers: { 'X-CSRFToken': getCsrfToken() } });
        const data = await res.json();
        if (data.status === 'success') {
          closeEditAnggotaModal();
          showToast('Sukses', data.message);
          setTimeout(() => window.location.reload(), 1000);
        } else {
          showToast('Error', data.message);
          btn.disabled = false;
          btn.innerHTML = '<i class="fa-solid fa-floppy-disk"></i> Simpan Perubahan';
        }
      } catch(err) {
        showToast('Error', 'Gagal memperbarui data mahasiswa.');
        btn.disabled = false;
        btn.innerHTML = '<i class="fa-solid fa-floppy-disk"></i> Simpan Perubahan';
      }
    }

    // 4. STRUKTUR KEPENGURUSAN
    function filterStrukturByPeriod(periodeId) {
      const items = document.querySelectorAll('.struktur-item');
      items.forEach(el => {
        const p = el.getAttribute('data-periode-id');
        if (periodeId === 'all' || p === String(periodeId)) {
          el.style.display = '';
        } else {
          el.style.display = 'none';
        }
      });
    }

    async function handleAddStrukturSubmit(e) {
      e.preventDefault();
      const formData = new FormData();
      formData.append('nama', document.getElementById('str-nama').value);
      formData.append('nim', document.getElementById('str-nim').value);
      formData.append('divisi', document.getElementById('str-divisi').value);
      formData.append('jabatan', document.getElementById('str-jabatan').value);
      formData.append('bio', document.getElementById('str-bio').value);
      formData.append('periode_id', document.getElementById('str-periode').value);
      const foto = document.getElementById('str-foto');
      if (foto && foto.files[0]) formData.append('foto', foto.files[0]);

      showToast('Menyimpan...', 'Menyimpan pengurus ke periode kepengurusan...');
      try {
        addCsrfToFormData(formData);
        const res = await fetch('/admin-api/struktur/tambah/', { method: 'POST', body: formData, headers: { 'X-CSRFToken': getCsrfToken() } });
        const data = await res.json();
        if (data.status === 'success') {
          closeAddStrukturModal();
          showToast('Sukses', data.message);
          setTimeout(() => window.location.reload(), 1000);
        } else {
          showToast('Error', data.message);
        }
      } catch(err) {
        showToast('Error', 'Gagal menyimpan struktur.');
      }
    }

    function openEditStrukturModal(id, nama, nim, divisi, jabatan, urutan, bio, periodeId) {
      document.getElementById('edit-str-id').value = id;
      document.getElementById('edit-str-nama').value = nama;
      document.getElementById('edit-str-nim').value = nim;
      document.getElementById('edit-str-divisi').value = divisi;
      document.getElementById('edit-str-jabatan').value = jabatan;
      document.getElementById('edit-str-urutan').value = urutan || 0;
      document.getElementById('edit-str-bio').value = bio || '';
      if (periodeId) {
        document.getElementById('edit-str-periode').value = periodeId;
      }
      const preview = document.getElementById('edit-str-foto-preview');
      const imgEl = document.getElementById('str-foto-img-' + id);
      if (preview && imgEl) preview.src = imgEl.src;
      document.getElementById('modal-edit-struktur').classList.remove('hidden');
    }

    function closeEditStrukturModal() {
      document.getElementById('modal-edit-struktur').classList.add('hidden');
    }

    async function handleEditStrukturSubmit(e) {
      e.preventDefault();
      const id = document.getElementById('edit-str-id').value;
      const formData = new FormData();
      formData.append('nama', document.getElementById('edit-str-nama').value);
      formData.append('nim', document.getElementById('edit-str-nim').value);
      formData.append('divisi', document.getElementById('edit-str-divisi').value);
      formData.append('jabatan', document.getElementById('edit-str-jabatan').value);
      formData.append('urutan', document.getElementById('edit-str-urutan').value);
      formData.append('bio', document.getElementById('edit-str-bio').value);
      formData.append('periode_id', document.getElementById('edit-str-periode').value);
      const foto = document.getElementById('edit-str-foto');
      if (foto && foto.files[0]) formData.append('foto', foto.files[0]);

      const btn = document.getElementById('btn-update-str');
      btn.disabled = true;
      btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Menyimpan...';
      showToast('Menyimpan...', 'Memperbarui data pengurus...');
      try {
        addCsrfToFormData(formData);
        const res = await fetch('/admin-api/struktur/edit/' + id + '/', { method: 'POST', body: formData, headers: { 'X-CSRFToken': getCsrfToken() } });
        const data = await res.json();
        if (data.status === 'success') {
          closeEditStrukturModal();
          showToast('Sukses', data.message);
          setTimeout(() => window.location.reload(), 1000);
        } else {
          showToast('Error', data.message);
          btn.disabled = false;
          btn.innerHTML = 'Simpan Perubahan';
        }
      } catch(err) {
        showToast('Error', 'Gagal memperbarui pengurus.');
        btn.disabled = false;
        btn.innerHTML = 'Simpan Perubahan';
      }
    }

    async function deleteStruktur(id) {
      if (!confirm('Hapus pejabat struktural ini?')) return;
      try {
        const res = await fetch('/admin-api/struktur/hapus/' + id + '/', { method: 'POST', headers: { 'X-CSRFToken': getCsrfToken() } });
        const data = await res.json();
        if (data.status === 'success') {
          const card = document.getElementById('struktur-card-' + id);
          if (card) card.remove();
          showToast('Dihapus', data.message);
        }
      } catch(err) {
        showToast('Error', 'Gagal menghapus.');
      }
    }

    // ==================== DIVISI STRUKTUR CRUD ====================
    function openManageDivisiModal() {
      resetDivisiForm();
      document.getElementById('modal-manage-divisi').classList.remove('hidden');
      refreshDivisiList();
    }
    function closeManageDivisiModal() {
      document.getElementById('modal-manage-divisi').classList.add('hidden');
    }
    function resetDivisiForm() {
      document.getElementById('div-id').value = '';
      document.getElementById('div-kode').value = '';
      document.getElementById('div-nama').value = '';
      document.getElementById('div-deskripsi').value = '';
      document.getElementById('div-urutan').value = '0';
      document.getElementById('div-mode-title').innerHTML = '<i class="fa-solid fa-plus-circle text-indigo-600"></i> Tambah Divisi Baru';
      document.getElementById('btn-save-divisi').innerHTML = '<i class="fa-solid fa-check"></i> Simpan Divisi';
      document.getElementById('btn-cancel-edit-div').classList.add('hidden');
    }
    async function refreshDivisiList() {
      try {
        const res = await fetch('/admin-api/divisi-struktur/list/');
        const json = await res.json();
        if (json.status === 'success') {
          const tbody = document.getElementById('divisi-table-body');
          const selectAdd = document.getElementById('str-divisi');
          const selectEdit = document.getElementById('edit-str-divisi');
          const currentAdd = selectAdd ? selectAdd.value : '';
          const currentEdit = selectEdit ? selectEdit.value : '';

          if (json.data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="py-4 text-center text-slate-400">Belum ada divisi.</td></tr>';
          } else {
            tbody.innerHTML = json.data.map(d => `
              <tr id="div-row-${d.id}" class="hover:bg-slate-50">
                <td class="py-2.5 px-3 font-mono font-bold text-indigo-700 uppercase">${escapeHtml(d.kode)}</td>
                <td class="py-2.5 px-3 font-bold text-brand-navy">${escapeHtml(d.nama)}</td>
                <td class="py-2.5 px-3 text-slate-500 max-w-xs truncate">${escapeHtml(d.deskripsi || '-')}</td>
                <td class="py-2.5 px-3 text-center font-mono text-slate-400">${d.urutan}</td>
                <td class="py-2.5 px-3 text-center font-mono font-bold text-brand-navy">${d.total_pengurus || 0}</td>
                <td class="py-2.5 px-3 text-center">
                  <div class="flex items-center justify-center gap-1.5">
                    <button type="button" onclick="editDivisi(${d.id})" class="p-1 text-blue-600 hover:bg-blue-50 rounded" title="Edit">
                      <i class="fa-solid fa-pen-to-square"></i>
                    </button>
                    <button type="button" onclick="deleteDivisi(${d.id})" class="p-1 text-rose-600 hover:bg-rose-50 rounded" title="Hapus">
                      <i class="fa-solid fa-trash-can"></i>
                    </button>
                  </div>
                </td>
              </tr>
            `).join('');

            const optionsHtml = json.data.map(d => `<option value="${escapeHtml(d.kode)}">${escapeHtml(d.nama)}</option>`).join('');
            if (selectAdd) selectAdd.innerHTML = optionsHtml;
            if (selectEdit) selectEdit.innerHTML = optionsHtml;
            if (selectAdd && currentAdd) selectAdd.value = currentAdd;
            if (selectEdit && currentEdit) selectEdit.value = currentEdit;
          }
        }
      } catch(e) {
        console.error('Error refreshing divisi list:', e);
      }
    }
    async function handleSaveDivisi(e) {
      e.preventDefault();
      const id = document.getElementById('div-id').value;
      const kode = document.getElementById('div-kode').value.trim();
      const nama = document.getElementById('div-nama').value.trim();
      const deskripsi = document.getElementById('div-deskripsi').value.trim();
      const urutan = document.getElementById('div-urutan').value;

      const formData = new FormData();
      formData.append('kode', kode);
      formData.append('nama', nama);
      formData.append('deskripsi', deskripsi);
      formData.append('urutan', urutan);
      addCsrfToFormData(formData);

      const url = id ? `/admin-api/divisi-struktur/edit/${id}/` : '/admin-api/divisi-struktur/tambah/';
      showToast('Menyimpan...', 'Menyimpan divisi struktur...');
      try {
        const res = await fetch(url, { method: 'POST', body: formData, headers: { 'X-CSRFToken': getCsrfToken() } });
        const json = await res.json();
        if (json.status === 'success') {
          showToast('Sukses', json.message);
          resetDivisiForm();
          refreshDivisiList();
        } else {
          showToast('Error', json.message || 'Gagal menyimpan divisi.');
        }
      } catch(err) {
        showToast('Error', 'Gagal menghubungi server.');
      }
    }
    async function editDivisi(id) {
      try {
        const res = await fetch(`/admin-api/divisi-struktur/edit/${id}/`);
        const json = await res.json();
        if (json.status === 'success' && json.data) {
          const d = json.data;
          document.getElementById('div-id').value = d.id;
          document.getElementById('div-kode').value = d.kode || '';
          document.getElementById('div-nama').value = d.nama || '';
          document.getElementById('div-deskripsi').value = d.deskripsi || '';
          document.getElementById('div-urutan').value = d.urutan || 0;
          document.getElementById('div-mode-title').innerHTML = '<i class="fa-solid fa-pen-to-square text-indigo-600"></i> Edit Divisi';
          document.getElementById('btn-save-divisi').innerHTML = '<i class="fa-solid fa-check"></i> Simpan Perubahan';
          document.getElementById('btn-cancel-edit-div').classList.remove('hidden');
          document.getElementById('div-nama').focus();
        }
      } catch(err) {
        showToast('Error', 'Gagal memuat detail divisi.');
      }
    }
    async function deleteDivisi(id) {
      if (!confirm('Hapus divisi ini? Pejabat struktur terkait tidak akan terhapus.')) return;
      try {
        const res = await fetch(`/admin-api/divisi-struktur/hapus/${id}/`, { method: 'POST', headers: { 'X-CSRFToken': getCsrfToken() } });
        const json = await res.json();
        if (json.status === 'success') {
          showToast('Sukses', json.message);
          refreshDivisiList();
        } else {
          showToast('Error', json.message || 'Gagal menghapus divisi.');
        }
      } catch(err) {
        showToast('Error', 'Gagal menghubungi server.');
      }
    }

    // 4B. ARSIP PERIODE KEPENGURUSAN (CRUD)
    function openAddArsipModal() {
      document.getElementById('modal-add-arsip').classList.remove('hidden');
    }

    function closeAddArsipModal() {
      document.getElementById('modal-add-arsip').classList.add('hidden');
    }

    async function handleAddArsipSubmit(e) {
      e.preventDefault();
      const formData = new FormData();
      formData.append('tahun_periode', document.getElementById('arsip-add-tahun').value);
      formData.append('nama_kabinet', document.getElementById('arsip-add-kabinet').value);
      formData.append('masa_bakti', document.getElementById('arsip-add-masa').value);
      formData.append('sk_rektor', document.getElementById('arsip-add-sk').value);
      formData.append('nama_ketua', document.getElementById('arsip-add-ketua').value);
      formData.append('nim_ketua', document.getElementById('arsip-add-nim-ketua').value);
      formData.append('nama_wakil', document.getElementById('arsip-add-wakil').value);
      formData.append('nim_wakil', document.getElementById('arsip-add-nim-wakil').value);
      formData.append('nama_sekretaris', document.getElementById('arsip-add-sekretaris').value);
      formData.append('nama_bendahara', document.getElementById('arsip-add-bendahara').value);
      formData.append('deskripsi', document.getElementById('arsip-add-deskripsi').value);
      formData.append('aktif', document.getElementById('arsip-add-aktif').checked ? 'true' : 'false');

      const btn = document.getElementById('btn-save-arsip');
      btn.disabled = true;
      btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Menyimpan...';
      showToast('Menyimpan...', 'Menyimpan arsip periode ke database...');
      try {
        addCsrfToFormData(formData);
        const res = await fetch('/admin-api/arsip/tambah/', { method: 'POST', body: formData, headers: { 'X-CSRFToken': getCsrfToken() } });
        const data = await res.json();
        if (data.status === 'success') {
          closeAddArsipModal();
          showToast('Sukses', data.message);
          setTimeout(() => window.location.reload(), 1000);
        } else {
          showToast('Error', data.message);
          btn.disabled = false;
          btn.innerHTML = 'Simpan Periode';
        }
      } catch(err) {
        showToast('Error', 'Gagal menyimpan arsip periode.');
        btn.disabled = false;
        btn.innerHTML = 'Simpan Periode';
      }
    }

    function openEditArsipModal(id, tahun, kabinet, masa, sk, ketua, nimKetua, wakil, nimWakil, sek, bend, desc, aktif, orderIndex) {
      document.getElementById('arsip-edit-id').value = id;
      document.getElementById('arsip-edit-tahun').value = tahun;
      document.getElementById('arsip-edit-kabinet').value = kabinet;
      document.getElementById('arsip-edit-masa').value = (masa && masa !== 'None') ? masa : '';
      document.getElementById('arsip-edit-sk').value = (sk && sk !== 'None') ? sk : '';
      document.getElementById('arsip-edit-ketua').value = ketua;
      document.getElementById('arsip-edit-nim-ketua').value = (nimKetua && nimKetua !== 'None') ? nimKetua : '';
      document.getElementById('arsip-edit-wakil').value = (wakil && wakil !== 'None') ? wakil : '';
      document.getElementById('arsip-edit-nim-wakil').value = (nimWakil && nimWakil !== 'None') ? nimWakil : '';
      document.getElementById('arsip-edit-sekretaris').value = (sek && sek !== 'None') ? sek : '';
      document.getElementById('arsip-edit-bendahara').value = (bend && bend !== 'None') ? bend : '';
      document.getElementById('arsip-edit-deskripsi').value = (desc && desc !== 'None') ? desc : '';
      document.getElementById('arsip-edit-aktif').checked = Boolean(aktif);
      document.getElementById('modal-edit-arsip').classList.remove('hidden');
    }

    function closeEditArsipModal() {
      document.getElementById('modal-edit-arsip').classList.add('hidden');
    }

    async function handleEditArsipSubmit(e) {
      e.preventDefault();
      const id = document.getElementById('arsip-edit-id').value;
      const formData = new FormData();
      formData.append('tahun_periode', document.getElementById('arsip-edit-tahun').value);
      formData.append('nama_kabinet', document.getElementById('arsip-edit-kabinet').value);
      formData.append('masa_bakti', document.getElementById('arsip-edit-masa').value);
      formData.append('sk_rektor', document.getElementById('arsip-edit-sk').value);
      formData.append('nama_ketua', document.getElementById('arsip-edit-ketua').value);
      formData.append('nim_ketua', document.getElementById('arsip-edit-nim-ketua').value);
      formData.append('nama_wakil', document.getElementById('arsip-edit-wakil').value);
      formData.append('nim_wakil', document.getElementById('arsip-edit-nim-wakil').value);
      formData.append('nama_sekretaris', document.getElementById('arsip-edit-sekretaris').value);
      formData.append('nama_bendahara', document.getElementById('arsip-edit-bendahara').value);
      formData.append('deskripsi', document.getElementById('arsip-edit-deskripsi').value);
      formData.append('aktif', document.getElementById('arsip-edit-aktif').checked ? 'true' : 'false');

      const btn = document.getElementById('btn-update-arsip');
      btn.disabled = true;
      btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Menyimpan...';
      showToast('Menyimpan...', 'Memperbarui arsip periode...');
      try {
        addCsrfToFormData(formData);
        const res = await fetch('/admin-api/arsip/edit/' + id + '/', { method: 'POST', body: formData, headers: { 'X-CSRFToken': getCsrfToken() } });
        const data = await res.json();
        if (data.status === 'success') {
          closeEditArsipModal();
          showToast('Sukses', data.message);
          setTimeout(() => window.location.reload(), 1000);
        } else {
          showToast('Error', data.message);
          btn.disabled = false;
          btn.innerHTML = 'Simpan Perubahan';
        }
      } catch(err) {
        showToast('Error', 'Gagal memperbarui arsip periode.');
        btn.disabled = false;
        btn.innerHTML = 'Simpan Perubahan';
      }
    }

    async function deleteArsip(id) {
      if (!confirm('Hapus arsip periode kepengurusan ini? Data pengurus dalam periode ini juga akan terhapus.')) return;
      try {
        const res = await fetch('/admin-api/arsip/hapus/' + id + '/', { method: 'POST', headers: { 'X-CSRFToken': getCsrfToken() } });
        const data = await res.json();
        if (data.status === 'success') {
          const card = document.getElementById('arsip-card-' + id);
          if (card) card.remove();
          showToast('Dihapus', data.message);
          setTimeout(() => window.location.reload(), 800);
        } else {
          showToast('Error', data.message);
        }
      } catch(err) {
        showToast('Error', 'Gagal menghapus arsip periode.');
      }
    }

    // 5. ASPIRASI
    async function updateAspirasiStatus(id, st) {
      const formData = new FormData();
      formData.append('status', st);
      formData.append('tanggapan', 'Aspirasi telah ditindaklanjuti dan diselesaikan oleh pengurus HIMA.');
      try {
        addCsrfToFormData(formData);
        const res = await fetch('/admin-api/aspirasi/update/' + id + '/', { method: 'POST', body: formData, headers: { 'X-CSRFToken': getCsrfToken() } });
        const data = await res.json();
        showToast('Aspirasi Diperbarui', data.message);
        setTimeout(() => window.location.reload(), 800);
      } catch(err) {
        showToast('Error', 'Gagal update status aspirasi.');
      }
    }

    async function deleteAspirasi(id) {
      if (!confirm('Hapus pesan aspirasi ini?')) return;
      try {
        const res = await fetch('/admin-api/aspirasi/hapus/' + id + '/', { method: 'POST', headers: { 'X-CSRFToken': getCsrfToken() } });
        const data = await res.json();
        if (data.status === 'success') {
          const card = document.getElementById('aspirasi-card-' + id);
          if (card) card.remove();
          showToast('Dihapus', data.message);
        }
      } catch(err) {
        showToast('Error', 'Gagal menghapus.');
      }
    }

    // 6. PROKER
    async function handleAddProkerSubmit(e) {
      e.preventDefault();
      const formData = new FormData();
      formData.append('nama', document.getElementById('prk-nama').value);
      formData.append('divisi', document.getElementById('prk-divisi').value);
      formData.append('status', document.getElementById('prk-status').value);
      formData.append('waktu_info', document.getElementById('prk-waktu').value);
      const lokasiEl = document.getElementById('prk-lokasi');
      if (lokasiEl) formData.append('lokasi', lokasiEl.value);
      const targetEl = document.getElementById('prk-target');
      if (targetEl) formData.append('target_peserta', targetEl.value);
      formData.append('deskripsi', document.getElementById('prk-deskripsi').value);
      const banner = document.getElementById('prk-banner');
      if (banner && banner.files[0]) formData.append('banner', banner.files[0]);

      showToast('Menyimpan...', 'Menyimpan program kerja...');
      try {
        addCsrfToFormData(formData);
        const res = await fetch('/admin-api/proker/tambah/', { method: 'POST', body: formData, headers: { 'X-CSRFToken': getCsrfToken() } });
        const data = await res.json();
        if (data.status === 'success') {
          closeAddProkerModal();
          showToast('Sukses', data.message);
          setTimeout(() => window.location.reload(), 1000);
        } else {
          showToast('Error', data.message || 'Gagal menyimpan proker.');
        }
      } catch(err) {
        showToast('Error', 'Gagal menyimpan proker.');
      }
    }

    async function openEditProkerModal(id) {
      showToast('Memuat...', 'Mengambil data program kerja...');
      try {
        const res = await fetch('/admin-api/proker/edit/' + id + '/');
        const json = await res.json();
        if (json.status === 'success' && json.data) {
          const d = json.data;
          document.getElementById('edit-prk-id').value = d.id;
          document.getElementById('edit-prk-nama').value = d.nama || '';
          document.getElementById('edit-prk-divisi').value = d.divisi || 'Diklat & Brevet';
          document.getElementById('edit-prk-status').value = d.status || 'Terjadwal';
          document.getElementById('edit-prk-waktu').value = d.waktu_info || '';
          document.getElementById('edit-prk-lokasi').value = d.lokasi || '';
          document.getElementById('edit-prk-target').value = d.target_peserta || '';
          document.getElementById('edit-prk-deskripsi').value = d.deskripsi || '';
          document.getElementById('edit-prk-banner').value = '';
          const preview = document.getElementById('edit-prk-banner-preview');
          if (preview) {
            if (d.banner) {
              preview.src = d.banner;
              preview.classList.remove('hidden');
            } else {
              preview.classList.add('hidden');
            }
          }
          document.getElementById('modal-edit-proker').classList.remove('hidden');
        } else {
          showToast('Error', 'Gagal memuat data program kerja.');
        }
      } catch(err) {
        showToast('Error', 'Gagal menghubungi server.');
      }
    }

    async function handleEditProkerSubmit(e) {
      e.preventDefault();
      const id = document.getElementById('edit-prk-id').value;
      const formData = new FormData();
      formData.append('nama', document.getElementById('edit-prk-nama').value);
      formData.append('divisi', document.getElementById('edit-prk-divisi').value);
      formData.append('status', document.getElementById('edit-prk-status').value);
      formData.append('waktu_info', document.getElementById('edit-prk-waktu').value);
      formData.append('lokasi', document.getElementById('edit-prk-lokasi').value);
      formData.append('target_peserta', document.getElementById('edit-prk-target').value);
      formData.append('deskripsi', document.getElementById('edit-prk-deskripsi').value);
      const banner = document.getElementById('edit-prk-banner');
      if (banner && banner.files[0]) formData.append('banner', banner.files[0]);

      const btn = document.getElementById('btn-update-proker');
      if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Menyimpan...';
      }
      showToast('Menyimpan...', 'Memperbarui program kerja...');

      try {
        addCsrfToFormData(formData);
        const res = await fetch('/admin-api/proker/edit/' + id + '/', {
          method: 'POST',
          body: formData,
          headers: { 'X-CSRFToken': getCsrfToken() }
        });
        const data = await res.json();
        if (data.status === 'success') {
          closeEditProkerModal();
          showToast('Sukses', data.message);
          setTimeout(() => window.location.reload(), 800);
        } else {
          showToast('Error', data.message || 'Gagal memperbarui program kerja.');
          if (btn) {
            btn.disabled = false;
            btn.innerHTML = 'Simpan Perubahan';
          }
        }
      } catch(err) {
        showToast('Error', 'Gagal menghubungi server.');
        if (btn) {
          btn.disabled = false;
          btn.innerHTML = 'Simpan Perubahan';
        }
      }
    }

    async function deleteProker(id) {
      if (!confirm('Hapus program kerja ini?')) return;
      try {
        const res = await fetch('/admin-api/proker/hapus/' + id + '/', { method: 'POST', headers: { 'X-CSRFToken': getCsrfToken() } });
        const data = await res.json();
        if (data.status === 'success') {
          const row = document.getElementById('proker-row-' + id);
          if (row) row.remove();
          showToast('Dihapus', data.message);
        }
      } catch(err) {
        showToast('Error', 'Gagal menghapus proker.');
      }
    }

    // 7. BERITA
    async function handleAddBeritaSubmit(e) {
      e.preventDefault();
      const formData = new FormData();
      formData.append('judul', document.getElementById('brt-judul').value);
      formData.append('kategori', document.getElementById('brt-kategori').value);
      formData.append('ringkasan', document.getElementById('brt-ringkasan').value);
      formData.append('isi', document.getElementById('brt-isi').value);
      const img = document.getElementById('brt-gambar');
      if (img.files[0]) formData.append('gambar', img.files[0]);

      showToast('Menyimpan...', 'Mengunggah gambar berita ke Cloudinary...');
      try {
        addCsrfToFormData(formData);
        const res = await fetch('/admin-api/berita/tambah/', { method: 'POST', body: formData, headers: { 'X-CSRFToken': getCsrfToken() } });
        const data = await res.json();
        if (data.status === 'success') {
          closeAddBeritaModal();
          showToast('Sukses', data.message);
          setTimeout(() => window.location.reload(), 1000);
        } else {
          showToast('Error', data.message || 'Gagal mempublikasikan berita.');
        }
      } catch(err) {
        showToast('Error', 'Gagal mempublikasikan berita.');
      }
    }

    async function deleteBerita(id) {
      if (!confirm('Hapus artikel berita ini?')) return;
      try {
        const res = await fetch('/admin-api/berita/hapus/' + id + '/', { method: 'POST', headers: { 'X-CSRFToken': getCsrfToken() } });
        const data = await res.json();
        if (data.status === 'success') {
          const row = document.getElementById('berita-row-' + id);
          if (row) row.remove();
          showToast('Dihapus', data.message);
        }
      } catch(err) {
        showToast('Error', 'Gagal menghapus berita.');
      }
    }

    async function openEditBeritaModal(id) {
      showToast('Memuat...', 'Mengambil data artikel berita...');
      try {
        const res = await fetch('/admin-api/berita/edit/' + id + '/');
        const json = await res.json();
        if (json.status === 'success' && json.data) {
          const d = json.data;
          document.getElementById('edit-brt-id').value = d.id;
          document.getElementById('edit-brt-judul').value = d.judul || '';
          document.getElementById('edit-brt-kategori').value = d.kategori || 'Perpajakan';
          document.getElementById('edit-brt-tanggal').value = d.tanggal || '';
          document.getElementById('edit-brt-penulis').value = d.penulis || '';
          document.getElementById('edit-brt-ringkasan').value = d.ringkasan || '';
          document.getElementById('edit-brt-isi').value = d.isi || '';
          document.getElementById('edit-brt-gambar-preview').src = d.gambar || '';
          document.getElementById('edit-brt-gambar').value = '';
          document.getElementById('modal-edit-berita').classList.remove('hidden');
        } else {
          showToast('Error', 'Gagal memuat data berita.');
        }
      } catch(err) {
        showToast('Error', 'Gagal menghubungi server.');
      }
    }

    async function handleEditBeritaSubmit(e) {
      e.preventDefault();
      const id = document.getElementById('edit-brt-id').value;
      const formData = new FormData();
      formData.append('judul', document.getElementById('edit-brt-judul').value);
      formData.append('kategori', document.getElementById('edit-brt-kategori').value);
      formData.append('tanggal', document.getElementById('edit-brt-tanggal').value);
      formData.append('penulis', document.getElementById('edit-brt-penulis').value);
      formData.append('ringkasan', document.getElementById('edit-brt-ringkasan').value);
      formData.append('isi', document.getElementById('edit-brt-isi').value);
      const img = document.getElementById('edit-brt-gambar');
      if (img.files[0]) formData.append('gambar', img.files[0]);

      const btn = document.getElementById('btn-update-berita');
      const origText = btn.innerHTML;
      btn.disabled = true;
      btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Menyimpan...';
      showToast('Menyimpan...', 'Memperbarui artikel berita...');

      try {
        addCsrfToFormData(formData);
        const res = await fetch('/admin-api/berita/edit/' + id + '/', {
          method: 'POST',
          body: formData,
          headers: { 'X-CSRFToken': getCsrfToken() }
        });
        const data = await res.json();
        if (data.status === 'success') {
          closeEditBeritaModal();
          showToast('Sukses', data.message);
          setTimeout(() => window.location.reload(), 800);
        } else {
          showToast('Error', data.message || 'Gagal memperbarui berita.');
          btn.disabled = false;
          btn.innerHTML = origText;
        }
      } catch(err) {
        showToast('Error', 'Terjadi kesalahan sistem.');
        btn.disabled = false;
        btn.innerHTML = origText;
      }
    }

    // 8. GALERI
    async function handleAddGaleriSubmit(e) {
      e.preventDefault();
      const formData = new FormData();
      formData.append('judul', document.getElementById('glr-judul').value);
      formData.append('kategori', document.getElementById('glr-kategori').value);
      const file = document.getElementById('glr-file');
      if (file.files[0]) formData.append('gambar', file.files[0]);

      showToast('Mengunggah...', 'Mengunggah foto resolusi tinggi ke Cloudinary Storage...');
      try {
        addCsrfToFormData(formData);
        const res = await fetch('/admin-api/galeri/tambah/', { method: 'POST', body: formData, headers: { 'X-CSRFToken': getCsrfToken() } });
        const data = await res.json();
        if (data.status === 'success') {
          closeAddGaleriModal();
          showToast('Sukses', data.message);
          setTimeout(() => window.location.reload(), 1000);
        } else {
          showToast('Error', data.message);
        }
      } catch(err) {
        showToast('Error', 'Gagal mengunggah foto.');
      }
    }

    async function deleteGaleri(id) {
      if (!confirm('Hapus foto dokumentasi ini?')) return;
      try {
        const res = await fetch('/admin-api/galeri/hapus/' + id + '/', { method: 'POST', headers: { 'X-CSRFToken': getCsrfToken() } });
        const data = await res.json();
        if (data.status === 'success') {
          const card = document.getElementById('galeri-card-' + id);
          if (card) card.remove();
          showToast('Dihapus', data.message);
        }
      } catch(err) {
        showToast('Error', 'Gagal menghapus foto.');
      }
    }

    async function openEditGaleriModal(id) {
      showToast('Memuat...', 'Mengambil data galeri...');
      try {
        const res = await fetch('/admin-api/galeri/edit/' + id + '/');
        const json = await res.json();
        if (json.status === 'success' && json.data) {
          const d = json.data;
          document.getElementById('edit-glr-id').value = d.id;
          document.getElementById('edit-glr-judul').value = d.judul || '';
          document.getElementById('edit-glr-kategori').value = d.kategori || 'Pelatihan Brevet';
          document.getElementById('edit-glr-tanggal').value = d.tanggal_kegiatan || '';
          document.getElementById('edit-glr-keterangan').value = d.keterangan || '';
          document.getElementById('edit-glr-gambar-preview').src = d.gambar || '';
          document.getElementById('edit-glr-file').value = '';
          document.getElementById('modal-edit-galeri').classList.remove('hidden');
        } else {
          showToast('Error', 'Gagal memuat data galeri.');
        }
      } catch(err) {
        showToast('Error', 'Gagal menghubungi server.');
      }
    }

    async function handleEditGaleriSubmit(e) {
      e.preventDefault();
      const id = document.getElementById('edit-glr-id').value;
      const formData = new FormData();
      formData.append('judul', document.getElementById('edit-glr-judul').value);
      formData.append('kategori', document.getElementById('edit-glr-kategori').value);
      formData.append('tanggal_kegiatan', document.getElementById('edit-glr-tanggal').value);
      formData.append('keterangan', document.getElementById('edit-glr-keterangan').value);
      const file = document.getElementById('edit-glr-file');
      if (file.files[0]) formData.append('gambar', file.files[0]);

      const btn = document.getElementById('btn-update-galeri');
      const origText = btn.innerHTML;
      btn.disabled = true;
      btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Menyimpan...';
      showToast('Menyimpan...', 'Memperbarui foto dokumentasi...');

      try {
        addCsrfToFormData(formData);
        const res = await fetch('/admin-api/galeri/edit/' + id + '/', {
          method: 'POST',
          body: formData,
          headers: { 'X-CSRFToken': getCsrfToken() }
        });
        const data = await res.json();
        if (data.status === 'success') {
          closeEditGaleriModal();
          showToast('Sukses', data.message);
          setTimeout(() => window.location.reload(), 800);
        } else {
          showToast('Error', data.message || 'Gagal memperbarui galeri.');
          btn.disabled = false;
          btn.innerHTML = origText;
        }
      } catch(err) {
        showToast('Error', 'Terjadi kesalahan sistem.');
        btn.disabled = false;
        btn.innerHTML = origText;
      }
    }

    // 9. PROFIL ORGANISASI
    async function handleUpdateProfilSubmit(e) {
      e.preventDefault();
      const form = e.target;
      const formData = new FormData(form);
      showToast('Menyimpan...', 'Memperbarui profil organisasi di Neon PostgreSQL & Cloudinary...');
      try {
        addCsrfToFormData(formData);
        const res = await fetch('/admin-api/profil/update/', { method: 'POST', body: formData, headers: { 'X-CSRFToken': getCsrfToken() } });
        const data = await res.json();
        if (data.status === 'success') {
          showToast('Sukses', data.message);
          setTimeout(() => window.location.reload(), 1000);
        } else {
          showToast('Error', data.message || 'Gagal memperbarui profil.');
        }
      } catch(err) {
        showToast('Error', 'Gagal memperbarui profil.');
      }
    }

    // 10. MULTI ADMIN
    async function handleAddUserSubmit(e) {
      e.preventDefault();
      const formData = new FormData();
      formData.append('nama', document.getElementById('usr-nama').value);
      formData.append('username', document.getElementById('usr-username').value);
      formData.append('email', document.getElementById('usr-email').value);
      formData.append('password', document.getElementById('usr-pass').value);
      formData.append('role', document.getElementById('usr-role').value);

      try {
        addCsrfToFormData(formData);
        const res = await fetch('/admin-api/user/tambah/', { method: 'POST', body: formData, headers: { 'X-CSRFToken': getCsrfToken() } });
        const data = await res.json();
        if (data.status === 'success') {
          closeAddUserModal();
          showToast('Sukses', data.message);
          setTimeout(() => window.location.reload(), 1000);
        } else {
          showToast('Error', data.message);
        }
      } catch(err) {
        showToast('Error', 'Gagal membuat akun.');
      }
    }

    async function deleteUser(id) {
      if (!confirm('Hapus akun pengelola ini?')) return;
      try {
        const res = await fetch('/admin-api/user/hapus/' + id + '/', { method: 'POST', headers: { 'X-CSRFToken': getCsrfToken() } });
        const data = await res.json();
        if (data.status === 'success') {
          const row = document.getElementById('user-row-' + id);
          if (row) row.remove();
          showToast('Dihapus', data.message);
        } else {
          showToast('Error', data.message);
        }
      } catch(err) {
        showToast('Error', 'Gagal menghapus user.');
      }
    }


    // Initialize Chart.js
    window.addEventListener('DOMContentLoaded', () => {
      // 1. Chart Divisi Admin (Doughnut)
      const ctxDiv = document.getElementById('chartDivisiAdmin');
      if (ctxDiv) {
        new Chart(ctxDiv, {
          type: 'doughnut',
          data: {
            labels: ['BPH', 'Diklat & Brevet', 'Kajian & Riset', 'Humas & Tax Center', 'Media'],
            datasets: [{
              data: [4, 6, 4, 4, 3],
              backgroundColor: ['#002B5C', '#F5C400', '#10B981', '#3B82F6', '#8B5CF6'],
              borderWidth: 2,
              borderColor: '#ffffff'
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: { position: 'bottom', labels: { boxWidth: 10, font: { size: 9 } } }
            }
          }
        });
      }

      // 2. Chart Kegiatan Admin (Bar)
      const ctxKeg = document.getElementById('chartKegiatanAdmin');
      if (ctxKeg) {
        new Chart(ctxKeg, {
          type: 'bar',
          data: {
            labels: ['Sep', 'Okt', 'Nov', 'Des', 'Jan', 'Feb'],
            datasets: [{
              label: 'Program Terlaksana',
              data: [1, 2, 2, 1, 1, 1],
              backgroundColor: '#002B5C',
              borderRadius: 6
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
              y: { beginAtZero: true, grid: { color: '#f1f5f9' }, ticks: { stepSize: 1 } },
              x: { grid: { display: false } }
            },
            plugins: { legend: { display: false } }
          }
        });
      }

      // 3. Chart Kas Admin (Bar Arus Kas)
      const ctxKas = document.getElementById('chartKasAdmin');
      if (ctxKas) {
        new Chart(ctxKas, {
          type: 'bar',
          data: {
            labels: ['Sep', 'Okt', 'Nov'],
            datasets: [
              {
                label: 'Masuk (Jt)',
                data: [40.4, 13.8, 0],
                backgroundColor: '#10B981',
                borderRadius: 4
              },
              {
                label: 'Keluar (Jt)',
                data: [3.45, 6.8, 6.8],
                backgroundColor: '#EF4444',
                borderRadius: 4
              }
            ]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
              y: { beginAtZero: true, grid: { color: '#f1f5f9' } },
              x: { grid: { display: false } }
            },
            plugins: {
              legend: { position: 'bottom', labels: { boxWidth: 10, font: { size: 9 } } }
            }
          }
        });
      }

      // 4. Charts Aspirasi Mahasiswa
      try {
        const aspData = window.ASPIRASI_CHART_DATA || {};
        
        // Status Doughnut Chart
        const ctxAspSt = document.getElementById('chartAspirasiStatus');
        if (ctxAspSt) {
          new Chart(ctxAspSt, {
            type: 'doughnut',
            data: {
              labels: aspData.status_labels || ['Pending', 'Diproses', 'Ditindaklanjuti', 'Selesai'],
              datasets: [{
                data: aspData.status_values || [0, 0, 0, 0],
                backgroundColor: ['#F59E0B', '#3B82F6', '#8B5CF6', '#10B981'],
                borderWidth: 2,
                borderColor: '#ffffff'
              }]
            },
            options: {
              responsive: true,
              maintainAspectRatio: false,
              plugins: {
                legend: { position: 'bottom', labels: { boxWidth: 10, font: { size: 9 } } }
              }
            }
          });
        }

        // Kategori Bar Chart
        const ctxAspKat = document.getElementById('chartAspirasiKategori');
        if (ctxAspKat) {
          new Chart(ctxAspKat, {
            type: 'bar',
            data: {
              labels: (aspData.kategori_labels && aspData.kategori_labels.length > 0) ? aspData.kategori_labels : ['Ormawa', 'Fasilitas', 'Akademik', 'Lainnya'],
              datasets: [{
                label: 'Jumlah Aspirasi',
                data: (aspData.kategori_values && aspData.kategori_values.length > 0) ? aspData.kategori_values : [0, 0, 0, 0],
                backgroundColor: '#7C3AED',
                borderRadius: 6
              }]
            },
            options: {
              responsive: true,
              maintainAspectRatio: false,
              scales: {
                y: { beginAtZero: true, ticks: { stepSize: 1 }, grid: { color: '#f1f5f9' } },
                x: { grid: { display: false } }
              },
              plugins: { legend: { display: false } }
            }
          });
        }

        // Rating Bar Chart
        const ctxAspRat = document.getElementById('chartAspirasiRating');
        if (ctxAspRat) {
          new Chart(ctxAspRat, {
            type: 'bar',
            data: {
              labels: ['⭐ 1', '⭐ 2', '⭐ 3', '⭐ 4', '⭐ 5'],
              datasets: [{
                label: 'Jumlah Penilai',
                data: aspData.rating_values || [0, 0, 0, 0, 0],
                backgroundColor: ['#EF4444', '#F97316', '#F59E0B', '#10B981', '#059669'],
                borderRadius: 6
              }]
            },
            options: {
              responsive: true,
              maintainAspectRatio: false,
              scales: {
                y: { beginAtZero: true, ticks: { stepSize: 1 }, grid: { color: '#f1f5f9' } },
                x: { grid: { display: false } }
              },
              plugins: { legend: { display: false } }
            }
          });
        }
      } catch(e) {
        console.warn('Aspirasi chart data error:', e);
      }
    });

    // ==================== KATEGORI BERITA CRUD ====================
    function openManageKategoriBeritaModal() {
      const modal = document.getElementById('modal-manage-kategori-berita');
      if (modal) modal.classList.remove('hidden');
      refreshKategoriBeritaList();
    }
    function closeManageKategoriBeritaModal() {
      const modal = document.getElementById('modal-manage-kategori-berita');
      if (modal) modal.classList.add('hidden');
      resetKategoriBeritaForm();
    }
    function resetKategoriBeritaForm() {
      const idEl = document.getElementById('kat-berita-id');
      if (idEl) idEl.value = '';
      const namaEl = document.getElementById('kat-berita-nama');
      if (namaEl) namaEl.value = '';
      const descEl = document.getElementById('kat-berita-deskripsi');
      if (descEl) descEl.value = '';
      const urutanEl = document.getElementById('kat-berita-urutan');
      if (urutanEl) urutanEl.value = '0';
      const titleEl = document.getElementById('kat-berita-mode-title');
      if (titleEl) titleEl.innerHTML = '<i class="fa-solid fa-plus-circle text-purple-600"></i> Tambah Kategori Berita';
      const btnSave = document.getElementById('btn-save-kat-berita');
      if (btnSave) btnSave.innerHTML = '<i class="fa-solid fa-plus"></i> Tambah Kategori';
      const btnCancel = document.getElementById('btn-cancel-edit-kat-berita');
      if (btnCancel) btnCancel.classList.add('hidden');
    }
    async function refreshKategoriBeritaList() {
      try {
        const res = await fetch('/admin-api/kategori-berita/list/');
        const json = await res.json();
        if (json.status === 'success') {
          const tbody = document.getElementById('kategori-berita-table-body');
          const selectAdd = document.getElementById('brt-kategori');
          const selectEdit = document.getElementById('edit-brt-kategori');
          const currentAdd = selectAdd ? selectAdd.value : '';
          const currentEdit = selectEdit ? selectEdit.value : '';

          if (tbody) {
            if (!json.data || json.data.length === 0) {
              tbody.innerHTML = '<tr><td colspan="5" class="py-4 text-center text-slate-400">Belum ada kategori berita.</td></tr>';
            } else {
              tbody.innerHTML = json.data.map(k => `
                <tr id="kat-berita-row-${k.id}" class="hover:bg-slate-50 border-b border-slate-100">
                  <td class="py-2.5 px-3 font-bold text-brand-navy">${escapeHtml(k.nama)}</td>
                  <td class="py-2.5 px-3 text-slate-500 max-w-xs truncate">${escapeHtml(k.deskripsi || '-')}</td>
                  <td class="py-2.5 px-3 text-center font-mono text-slate-400">${k.urutan}</td>
                  <td class="py-2.5 px-3 text-center font-mono font-bold text-purple-700">${k.total_berita || 0}</td>
                  <td class="py-2.5 px-3 text-center">
                    <div class="flex items-center justify-center gap-1.5">
                      <button type="button" onclick="editKategoriBerita(${k.id})" class="p-1 text-blue-600 hover:bg-blue-50 rounded" title="Edit">
                        <i class="fa-solid fa-pen-to-square"></i>
                      </button>
                      <button type="button" onclick="deleteKategoriBerita(${k.id})" class="p-1 text-rose-600 hover:bg-rose-50 rounded" title="Hapus">
                        <i class="fa-solid fa-trash-can"></i>
                      </button>
                    </div>
                  </td>
                </tr>
              `).join('');
            }
          }

          if (json.data && json.data.length > 0) {
            const optionsHtml = json.data.map(k => `<option value="${escapeHtml(k.nama)}">${escapeHtml(k.nama)}</option>`).join('');
            if (selectAdd) {
              selectAdd.innerHTML = optionsHtml;
              if (currentAdd) selectAdd.value = currentAdd;
            }
            if (selectEdit) {
              selectEdit.innerHTML = optionsHtml;
              if (currentEdit) selectEdit.value = currentEdit;
            }
          }
        }
      } catch(e) {
        console.error('Error refreshing kategori berita list:', e);
      }
    }
    async function handleSaveKategoriBerita(e) {
      e.preventDefault();
      const idEl = document.getElementById('kat-berita-id');
      const id = idEl ? idEl.value : '';
      const nama = (document.getElementById('kat-berita-nama').value || '').trim();
      const deskripsi = (document.getElementById('kat-berita-deskripsi').value || '').trim();
      const urutan = document.getElementById('kat-berita-urutan').value || 0;

      const formData = new FormData();
      formData.append('nama', nama);
      formData.append('deskripsi', deskripsi);
      formData.append('urutan', urutan);
      addCsrfToFormData(formData);

      const url = id ? `/admin-api/kategori-berita/edit/${id}/` : '/admin-api/kategori-berita/tambah/';
      showToast('Menyimpan...', 'Menyimpan kategori berita...');
      try {
        const res = await fetch(url, { method: 'POST', body: formData, headers: { 'X-CSRFToken': getCsrfToken() } });
        const json = await res.json();
        if (json.status === 'success') {
          showToast('Sukses', json.message);
          resetKategoriBeritaForm();
          refreshKategoriBeritaList();
        } else {
          showToast('Error', json.message || 'Gagal menyimpan kategori.');
        }
      } catch(err) {
        showToast('Error', 'Gagal menghubungi server.');
      }
    }
    async function editKategoriBerita(id) {
      try {
        const res = await fetch(`/admin-api/kategori-berita/edit/${id}/`);
        const json = await res.json();
        if (json.status === 'success' && json.data) {
          const d = json.data;
          document.getElementById('kat-berita-id').value = d.id;
          document.getElementById('kat-berita-nama').value = d.nama || '';
          document.getElementById('kat-berita-deskripsi').value = d.deskripsi || '';
          document.getElementById('kat-berita-urutan').value = d.urutan || 0;
          document.getElementById('kat-berita-mode-title').innerHTML = '<i class="fa-solid fa-pen-to-square text-purple-600"></i> Edit Kategori Berita';
          document.getElementById('btn-save-kat-berita').innerHTML = '<i class="fa-solid fa-check"></i> Simpan Perubahan';
          document.getElementById('btn-cancel-edit-kat-berita').classList.remove('hidden');
          document.getElementById('kat-berita-nama').focus();
        }
      } catch(err) {
        showToast('Error', 'Gagal memuat detail kategori.');
      }
    }
    async function deleteKategoriBerita(id) {
      if (!confirm('Hapus kategori berita ini?')) return;
      try {
        const res = await fetch(`/admin-api/kategori-berita/hapus/${id}/`, { method: 'POST', headers: { 'X-CSRFToken': getCsrfToken() } });
        const json = await res.json();
        if (json.status === 'success') {
          showToast('Sukses', json.message);
          refreshKategoriBeritaList();
        } else {
          showToast('Error', json.message || 'Gagal menghapus kategori.');
        }
      } catch(err) {
        showToast('Error', 'Gagal menghubungi server.');
      }
    }

    // ==================== KATEGORI GALERI CRUD ====================
    function openManageKategoriGaleriModal() {
      const modal = document.getElementById('modal-manage-kategori-galeri');
      if (modal) modal.classList.remove('hidden');
      refreshKategoriGaleriList();
    }
    function closeManageKategoriGaleriModal() {
      const modal = document.getElementById('modal-manage-kategori-galeri');
      if (modal) modal.classList.add('hidden');
      resetKategoriGaleriForm();
    }
    function resetKategoriGaleriForm() {
      const idEl = document.getElementById('kat-galeri-id');
      if (idEl) idEl.value = '';
      const namaEl = document.getElementById('kat-galeri-nama');
      if (namaEl) namaEl.value = '';
      const descEl = document.getElementById('kat-galeri-deskripsi');
      if (descEl) descEl.value = '';
      const urutanEl = document.getElementById('kat-galeri-urutan');
      if (urutanEl) urutanEl.value = '0';
      const titleEl = document.getElementById('kat-galeri-mode-title');
      if (titleEl) titleEl.innerHTML = '<i class="fa-solid fa-plus-circle text-amber-600"></i> Tambah Kategori Galeri';
      const btnSave = document.getElementById('btn-save-kat-galeri');
      if (btnSave) btnSave.innerHTML = '<i class="fa-solid fa-plus"></i> Tambah Kategori';
      const btnCancel = document.getElementById('btn-cancel-edit-kat-galeri');
      if (btnCancel) btnCancel.classList.add('hidden');
    }
    async function refreshKategoriGaleriList() {
      try {
        const res = await fetch('/admin-api/kategori-galeri/list/');
        const json = await res.json();
        if (json.status === 'success') {
          const tbody = document.getElementById('kategori-galeri-table-body');
          const selectAdd = document.getElementById('glr-kategori');
          const selectEdit = document.getElementById('edit-glr-kategori');
          const currentAdd = selectAdd ? selectAdd.value : '';
          const currentEdit = selectEdit ? selectEdit.value : '';

          if (tbody) {
            if (!json.data || json.data.length === 0) {
              tbody.innerHTML = '<tr><td colspan="5" class="py-4 text-center text-slate-400">Belum ada kategori galeri.</td></tr>';
            } else {
              tbody.innerHTML = json.data.map(k => `
                <tr id="kat-galeri-row-${k.id}" class="hover:bg-slate-50 border-b border-slate-100">
                  <td class="py-2.5 px-3 font-bold text-brand-navy">${escapeHtml(k.nama)}</td>
                  <td class="py-2.5 px-3 text-slate-500 max-w-xs truncate">${escapeHtml(k.deskripsi || '-')}</td>
                  <td class="py-2.5 px-3 text-center font-mono text-slate-400">${k.urutan}</td>
                  <td class="py-2.5 px-3 text-center font-mono font-bold text-amber-600">${k.total_galeri || 0}</td>
                  <td class="py-2.5 px-3 text-center">
                    <div class="flex items-center justify-center gap-1.5">
                      <button type="button" onclick="editKategoriGaleri(${k.id})" class="p-1 text-blue-600 hover:bg-blue-50 rounded" title="Edit">
                        <i class="fa-solid fa-pen-to-square"></i>
                      </button>
                      <button type="button" onclick="deleteKategoriGaleri(${k.id})" class="p-1 text-rose-600 hover:bg-rose-50 rounded" title="Hapus">
                        <i class="fa-solid fa-trash-can"></i>
                      </button>
                    </div>
                  </td>
                </tr>
              `).join('');
            }
          }

          if (json.data && json.data.length > 0) {
            const optionsHtml = json.data.map(k => `<option value="${escapeHtml(k.nama)}">${escapeHtml(k.nama)}</option>`).join('');
            if (selectAdd) {
              selectAdd.innerHTML = optionsHtml;
              if (currentAdd) selectAdd.value = currentAdd;
            }
            if (selectEdit) {
              selectEdit.innerHTML = optionsHtml;
              if (currentEdit) selectEdit.value = currentEdit;
            }
          }
        }
      } catch(e) {
        console.error('Error refreshing kategori galeri list:', e);
      }
    }
    async function handleSaveKategoriGaleri(e) {
      e.preventDefault();
      const idEl = document.getElementById('kat-galeri-id');
      const id = idEl ? idEl.value : '';
      const nama = (document.getElementById('kat-galeri-nama').value || '').trim();
      const deskripsi = (document.getElementById('kat-galeri-deskripsi').value || '').trim();
      const urutan = document.getElementById('kat-galeri-urutan').value || 0;

      const formData = new FormData();
      formData.append('nama', nama);
      formData.append('deskripsi', deskripsi);
      formData.append('urutan', urutan);
      addCsrfToFormData(formData);

      const url = id ? `/admin-api/kategori-galeri/edit/${id}/` : '/admin-api/kategori-galeri/tambah/';
      showToast('Menyimpan...', 'Menyimpan kategori galeri...');
      try {
        const res = await fetch(url, { method: 'POST', body: formData, headers: { 'X-CSRFToken': getCsrfToken() } });
        const json = await res.json();
        if (json.status === 'success') {
          showToast('Sukses', json.message);
          resetKategoriGaleriForm();
          refreshKategoriGaleriList();
        } else {
          showToast('Error', json.message || 'Gagal menyimpan kategori.');
        }
      } catch(err) {
        showToast('Error', 'Gagal menghubungi server.');
      }
    }
    async function editKategoriGaleri(id) {
      try {
        const res = await fetch(`/admin-api/kategori-galeri/edit/${id}/`);
        const json = await res.json();
        if (json.status === 'success' && json.data) {
          const d = json.data;
          document.getElementById('kat-galeri-id').value = d.id;
          document.getElementById('kat-galeri-nama').value = d.nama || '';
          document.getElementById('kat-galeri-deskripsi').value = d.deskripsi || '';
          document.getElementById('kat-galeri-urutan').value = d.urutan || 0;
          document.getElementById('kat-galeri-mode-title').innerHTML = '<i class="fa-solid fa-pen-to-square text-amber-600"></i> Edit Kategori Galeri';
          document.getElementById('btn-save-kat-galeri').innerHTML = '<i class="fa-solid fa-check"></i> Simpan Perubahan';
          document.getElementById('btn-cancel-edit-kat-galeri').classList.remove('hidden');
          document.getElementById('kat-galeri-nama').focus();
        }
      } catch(err) {
        showToast('Error', 'Gagal memuat detail kategori.');
      }
    }
    async function deleteKategoriGaleri(id) {
      if (!confirm('Hapus kategori galeri ini?')) return;
      try {
        const res = await fetch(`/admin-api/kategori-galeri/hapus/${id}/`, { method: 'POST', headers: { 'X-CSRFToken': getCsrfToken() } });
        const json = await res.json();
        if (json.status === 'success') {
          showToast('Sukses', json.message);
          refreshKategoriGaleriList();
        } else {
          showToast('Error', json.message || 'Gagal menghapus kategori.');
        }
      } catch(err) {
        showToast('Error', 'Gagal menghubungi server.');
      }
    }
