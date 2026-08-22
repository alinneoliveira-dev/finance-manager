const API_BASE = '';  // vazio: front e API estão na mesma origem agora (mesma porta do Flask)

let tipoSelecionado = 'entrada';

const meses = ['janeiro','fevereiro','março','abril','maio','junho','julho',
               'agosto','setembro','outubro','novembro','dezembro'];

function formatarMoeda(valor) {
  return `R$ ${Number(valor).toFixed(2).replace('.', ',')}`;
}

function formatarData(dataISO) {
  const [ano, mes, dia] = dataISO.split('-');
  return `${dia}/${mes}/${ano}`;
}

function definirPeriodoAtual() {
  const hoje = new Date();
  document.getElementById('periodo-atual').textContent =
    `${meses[hoje.getMonth()]} de ${hoje.getFullYear()} — Atualizações em tempo real`;
}

// ---------- DASHBOARD ----------

async function carregarDashboard() {
  const res = await fetch(`${API_BASE}/api/dashboard`);
  const data = await res.json();

  document.getElementById('saldo-atual').textContent = formatarMoeda(data.saldo_atual);
  document.getElementById('total-entradas').textContent = formatarMoeda(data.total_entradas);
  document.getElementById('total-saidas').textContent = formatarMoeda(data.total_saidas);
}

// ---------- CATEGORIAS ----------

async function carregarCategoriasForm(tipo) {
  const res = await fetch(`${API_BASE}/api/categorias?tipo=${tipo}`);
  const categorias = await res.json();

  const select = document.getElementById('categoria');
  select.innerHTML = '<option value="">Selecionar categoria…</option>';
  categorias.forEach(cat => {
    const opt = document.createElement('option');
    opt.value = cat.id;
    opt.textContent = cat.nome;
    select.appendChild(opt);
  });
}

async function carregarCategoriasFiltro() {
  const res = await fetch(`${API_BASE}/api/categorias`);
  const categorias = await res.json();

  const select = document.getElementById('filtro-categoria');
  select.innerHTML = '<option value="">Todas as categorias</option>';
  categorias.forEach(cat => {
    const opt = document.createElement('option');
    opt.value = cat.id;
    opt.textContent = cat.nome;
    select.appendChild(opt);
  });
}

// ---------- TRANSAÇÕES ----------

function corComOpacidade(hex, alpha) {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

function renderizarTransacoes(transacoes) {
  const lista = document.getElementById('lista-transacoes');
  document.getElementById('total-transacoes').textContent = transacoes.length;

  if (transacoes.length === 0) {
    lista.innerHTML = '<p class="lista-vazia">Nenhuma transação encontrada.</p>';
    return;
  }

  lista.innerHTML = transacoes.map(t => {
    const sinal = t.tipo === 'entrada' ? '+' : '−';
    const seta = t.tipo === 'entrada' ? '↑' : '↓';
    const cor = t.categoria_cor || '#3B82F6';

    return `
      <div class="transacao-row">
        <div class="tx-icone ${t.tipo}">${seta}</div>
        <div class="tx-info">
          <div class="tx-desc">${t.descricao}</div>
          <div class="tx-meta">
            <span class="tx-data">${formatarData(t.data_transacao)}</span>
            ${t.categoria_nome ? `<span class="tx-tag" style="background:${corComOpacidade(cor, 0.15)}; color:${cor}">${t.categoria_nome}</span>` : ''}
          </div>
        </div>
        <div class="tx-valor ${t.tipo}">${sinal} ${formatarMoeda(t.valor)}</div>
      </div>
    `;
  }).join('');
}

async function carregarTransacoes() {
  const busca = document.getElementById('busca').value.trim();
  const tipo = document.getElementById('filtro-tipo').value;
  const categoriaId = document.getElementById('filtro-categoria').value;

  const params = new URLSearchParams();
  if (busca) params.set('busca', busca);
  if (tipo) params.set('tipo', tipo);
  if (categoriaId) params.set('categoria_id', categoriaId);

  const res = await fetch(`${API_BASE}/api/transacoes?${params.toString()}`);
  const data = await res.json();
  renderizarTransacoes(data.transacoes);
}

// ---------- FORMULÁRIO NOVA TRANSAÇÃO ----------

function configurarToggleTipo() {
  const botoes = document.querySelectorAll('.tipo-btn');
  botoes.forEach(btn => {
    btn.addEventListener('click', () => {
      botoes.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      tipoSelecionado = btn.dataset.tipo;
      carregarCategoriasForm(tipoSelecionado);
    });
  });
}

async function salvarTransacao(evento) {
  evento.preventDefault();
  const erroEl = document.getElementById('form-erro');
  erroEl.textContent = '';

  const payload = {
    descricao: document.getElementById('descricao').value.trim(),
    valor: parseFloat(document.getElementById('valor').value),
    tipo: tipoSelecionado,
    categoria_id: document.getElementById('categoria').value || null,
    data_transacao: document.getElementById('data-transacao').value
  };

  const res = await fetch(`${API_BASE}/api/transacoes`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  if (!res.ok) {
    const erro = await res.json();
    erroEl.textContent = erro.erro || 'Não foi possível salvar a transação.';
    return;
  }

  document.getElementById('form-transacao').reset();
  document.getElementById('data-transacao').valueAsDate = new Date();

  await Promise.all([carregarDashboard(), carregarTransacoes()]);
}

// ---------- INICIALIZAÇÃO ----------

document.addEventListener('DOMContentLoaded', async () => {
  definirPeriodoAtual();
  document.getElementById('data-transacao').valueAsDate = new Date();

  configurarToggleTipo();
  document.getElementById('form-transacao').addEventListener('submit', salvarTransacao);

  document.getElementById('busca').addEventListener('input', carregarTransacoes);
  document.getElementById('filtro-tipo').addEventListener('change', carregarTransacoes);
  document.getElementById('filtro-categoria').addEventListener('change', carregarTransacoes);

  await Promise.all([
    carregarDashboard(),
    carregarCategoriasForm(tipoSelecionado),
    carregarCategoriasFiltro(),
    carregarTransacoes()
  ]);
});
