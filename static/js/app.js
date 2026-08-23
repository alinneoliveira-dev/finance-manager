const API_BASE = '';  

let tipoSelecionado = 'entrada';

const meses = ['Janeiro','Fevereiro','Março','Abril','Maio','Junho','Julho',
               'Agosto','Setembro','Outubro','Novembro','Dezembro'];

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
    `${meses[hoje.getMonth()]} de ${hoje.getFullYear()}`;
}

//dashboard

async function carregarDashboard() {
  const res = await fetch(`${API_BASE}/api/dashboard`);
  const data = await res.json();

  document.getElementById('saldo-atual').textContent = formatarMoeda(data.saldo_atual);
  document.getElementById('total-entradas').textContent = formatarMoeda(data.total_entradas);
  document.getElementById('total-saidas').textContent = formatarMoeda(data.total_saidas);
}

//categorias

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

//transações

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

//forms nova transações

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


function configurarTrocaDeView() {
  document.querySelectorAll('.menu-item[data-view]').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.menu-item[data-view]').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      const view = btn.dataset.view;
      document.getElementById('view-dashboard').style.display = view === 'dashboard' ? '' : 'none';
      document.getElementById('view-categorias').style.display = view === 'categorias' ? '' : 'none';
      document.getElementById('view-limites').style.display = view === 'limites' ? '' : 'none';

      if (view === 'categorias') carregarListaCategorias();
      if (view === 'limites') carregarListaLimites();
    });
  });
}

//crud

let tipoCategoriaSelecionado = 'entrada';

async function carregarListaCategorias() {
  const res = await fetch(`${API_BASE}/api/categorias`);
  const categorias = await res.json();

  document.getElementById('total-categorias').textContent = categorias.length;
  const lista = document.getElementById('lista-categorias');

  if (categorias.length === 0) {
    lista.innerHTML = '<p class="lista-vazia">Nenhuma categoria cadastrada.</p>';
    return;
  }

  lista.innerHTML = categorias.map(cat => `
    <div class="transacao-row">
      <div class="tx-icone" style="background:${corComOpacidade(cat.cor, 0.15)}; color:${cat.cor}">●</div>
      <div class="tx-info">
        <div class="tx-desc">${cat.nome}</div>
        <div class="tx-meta"><span class="tx-data">${cat.tipo === 'entrada' ? 'Entrada' : 'Saída'}</span></div>
      </div>
      <button type="button" class="btn-excluir" data-id="${cat.id}">Excluir</button>
    </div>
  `).join('');

  lista.querySelectorAll('.btn-excluir').forEach(btn => {
    btn.addEventListener('click', () => excluirCategoria(btn.dataset.id));
  });
}

async function excluirCategoria(id) {
  const res = await fetch(`${API_BASE}/api/categorias/${id}`, { method: 'DELETE' });

  if (!res.ok) {
    const erro = await res.json();
    alert(erro.erro || 'Não foi possível excluir essa categoria.');
    return;
  }

  carregarListaCategorias();
}

function configurarFormCategoria() {
  document.querySelectorAll('[data-tipo-cat]').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('[data-tipo-cat]').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      tipoCategoriaSelecionado = btn.dataset.tipoCat;
    });
  });

  document.getElementById('form-categoria').addEventListener('submit', async (evento) => {
    evento.preventDefault();
    const erroEl = document.getElementById('form-erro-categoria');
    erroEl.textContent = '';

    const payload = {
      nome: document.getElementById('nome-categoria').value.trim(),
      tipo: tipoCategoriaSelecionado,
      cor: document.getElementById('cor-categoria').value
    };

    const res = await fetch(`${API_BASE}/api/categorias`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      const erro = await res.json();
      erroEl.textContent = erro.erro || 'Não foi possível salvar a categoria.';
      return;
    }

    document.getElementById('form-categoria').reset();
    carregarListaCategorias();
  });
}

//limites por categoria

async function carregarSelectLimite() {
  const res = await fetch(`${API_BASE}/api/categorias?tipo=saida`);
  const categorias = await res.json();

  const select = document.getElementById('categoria-limite');
  select.innerHTML = '<option value="">Selecionar categoria…</option>';
  categorias.forEach(cat => {
    const opt = document.createElement('option');
    opt.value = cat.id;
    opt.textContent = cat.nome;
    select.appendChild(opt);
  });
}

function classeBarraLimite(percentual) {
  if (percentual === null) return 'barra-neutra';
  if (percentual >= 100) return 'barra-estourada';
  if (percentual >= 80) return 'barra-alerta';
  return 'barra-ok';
}

async function carregarListaLimites() {
  const res = await fetch(`${API_BASE}/api/limites`);
  const data = await res.json();
  const lista = document.getElementById('lista-limites');

  if (data.limites.length === 0) {
    lista.innerHTML = '<p class="lista-vazia">Nenhuma categoria de saída cadastrada ainda.</p>';
    return;
  }

  lista.innerHTML = data.limites.map(l => {
    const semLimite = l.limite_mensal === null;
    const percentual = l.percentual !== null ? Math.min(l.percentual, 100) : 0;

    return `
      <div class="limite-row">
        <div class="limite-topo">
          <span class="tx-desc">${l.categoria_nome}</span>
          <span class="limite-valores">
            ${formatarMoeda(l.gasto_atual)} ${semLimite ? '' : `/ ${formatarMoeda(l.limite_mensal)}`}
          </span>
        </div>
        ${semLimite
          ? '<p class="limite-sem-valor">Nenhum limite definido ainda</p>'
          : `<div class="barra-fundo"><div class="barra-preenchida ${classeBarraLimite(l.percentual)}" style="width:${percentual}%"></div></div>
             <p class="limite-percentual">${l.percentual}% do limite usado</p>`
        }
      </div>
    `;
  }).join('');
}

function configurarFormLimite() {
  document.getElementById('form-limite').addEventListener('submit', async (evento) => {
    evento.preventDefault();
    const erroEl = document.getElementById('form-erro-limite');
    erroEl.textContent = '';

    const payload = {
      categoria_id: document.getElementById('categoria-limite').value,
      limite_mensal: parseFloat(document.getElementById('valor-limite').value)
    };

    if (!payload.categoria_id) {
      erroEl.textContent = 'Selecione uma categoria.';
      return;
    }

    const res = await fetch(`${API_BASE}/api/limites`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      const erro = await res.json();
      erroEl.textContent = erro.erro || 'Não foi possível salvar o limite.';
      return;
    }

    document.getElementById('form-limite').reset();
    carregarListaLimites();
  });
}


document.addEventListener('DOMContentLoaded', async () => {
  definirPeriodoAtual();
  document.getElementById('data-transacao').valueAsDate = new Date();

  configurarToggleTipo();
  document.getElementById('form-transacao').addEventListener('submit', salvarTransacao);

  document.getElementById('busca').addEventListener('input', carregarTransacoes);
  document.getElementById('filtro-tipo').addEventListener('change', carregarTransacoes);
  document.getElementById('filtro-categoria').addEventListener('change', carregarTransacoes);

  configurarTrocaDeView();
  configurarFormCategoria();
  configurarFormLimite();
  carregarSelectLimite();

  await Promise.all([
    carregarDashboard(),
    carregarCategoriasForm(tipoSelecionado),
    carregarCategoriasFiltro(),
    carregarTransacoes()
  ]);

  setInterval(() => {
    carregarDashboard();
    carregarTransacoes();
  }, 15000);
});
