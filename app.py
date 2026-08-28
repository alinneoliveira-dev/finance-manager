from datetime import date, datetime
from functools import wraps
import os
from flask import Flask, jsonify, render_template, request

# Importe seus modelos e o banco de dados (ajuste o caminho se necessário)
# Exemplo: from models import db, Categoria, Despesa
from routes.categorias import categorias_bp
from routes.dashboard import dashboard_bp
from routes.limites import limites_bp
from routes.transacoes import transacoes_bp

app = Flask(__name__)

app.register_blueprint(dashboard_bp)
app.register_blueprint(transacoes_bp)
app.register_blueprint(categorias_bp)
app.register_blueprint(limites_bp)


@app.route("/")
def index():
  return render_template("index.html")


# ---------------------------------------------------------------------------
# API para o bot do Telegram (ou qualquer outro cliente externo)
# ---------------------------------------------------------------------------
API_KEY = os.environ.get("BOT_API_KEY", "troque-esta-chave")


def exigir_api_key(func):
  @wraps(func)
  def wrapper(*args, **kwargs):
    chave_enviada = request.headers.get("X-API-Key")
    if chave_enviada != API_KEY:
      return jsonify({"erro": "não autorizado"}), 401
    return func(*args, **kwargs)

  return wrapper


@app.route("/api/categorias", methods=["GET"])
@exigir_api_key
def api_categorias():
  categorias = Categoria.query.order_by(Categoria.nome).all()
  return jsonify([{"id": c.id, "nome": c.nome} for c in categorias])


@app.route("/api/despesas", methods=["POST"])
@exigir_api_key
def api_criar_despesa():
  dados = request.get_json(silent=True) or {}
  descricao = (dados.get("descricao") or "").strip()
  categoria_id = dados.get("categoria_id")
  valor = dados.get("valor")
  data_str = dados.get("data")  # formato "YYYY-MM-DD", opcional (default hoje)

  if not descricao or not categoria_id or not valor:
    return (
        jsonify({"erro": "descricao, categoria_id e valor são obrigatórios"}),
        400,
    )

  categoria = Categoria.query.get(categoria_id)
  if not categoria:
    return jsonify({"erro": "categoria não encontrada"}), 404

  try:
    data_despesa = (
        datetime.strptime(data_str, "%Y-%m-%d").date()
        if data_str
        else date.today()
    )
    valor_float = float(str(valor).replace(",", "."))
  except (ValueError, TypeError):
    return jsonify({"erro": "valor ou data em formato inválido"}), 400

  nova = Despesa(
      descricao=descricao,
      categoria_id=categoria_id,
      valor=valor_float,
      data=data_despesa,
  )
  db.session.add(nova)
  db.session.commit()

  return (
      jsonify({
          "id": nova.id,
          "descricao": nova.descricao,
          "categoria": categoria.nome,
          "valor": float(nova.valor),
          "data": nova.data.isoformat(),
      }),
      201,
  )


if __name__ == "__main__":
  app.run(debug=True, port=5000)