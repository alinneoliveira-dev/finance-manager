import os
from datetime import date, datetime
from functools import wraps

from flask import Blueprint, request, jsonify

from db import db, Categoria, Despesa 

api_bot_bp = Blueprint("api_bot", __name__, url_prefix="/api")

API_KEY = os.environ.get("BOT_API_KEY", "chave")


def exigir_api_key(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        chave_enviada = request.headers.get("X-API-Key")
        if chave_enviada != API_KEY:
            return jsonify({"erro": "não autorizado"}), 401
        return func(*args, **kwargs)
    return wrapper


@api_bot_bp.route("/categorias", methods=["GET"])
@exigir_api_key
def api_categorias():
    categorias = Categoria.query.order_by(Categoria.nome).all()
    return jsonify([{"id": c.id, "nome": c.nome} for c in categorias])


@api_bot_bp.route("/despesas", methods=["POST"])
@exigir_api_key
def api_criar_despesa():
    dados = request.get_json(silent=True) or {}
    descricao = (dados.get("descricao") or "").strip()
    categoria_id = dados.get("categoria_id")
    valor = dados.get("valor")
    data_str = dados.get("data") 

    if not descricao or not categoria_id or not valor:
        return jsonify({"erro": "descricao, categoria_id e valor são obrigatórios"}), 400

    categoria = Categoria.query.get(categoria_id)
    if not categoria:
        return jsonify({"erro": "categoria não encontrada"}), 404

    try:
        data_despesa = (
            datetime.strptime(data_str, "%Y-%m-%d").date() if data_str else date.today()
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

    return jsonify({
        "id": nova.id,
        "descricao": nova.descricao,
        "categoria": categoria.nome,
        "valor": float(nova.valor),
        "data": nova.data.isoformat(),
    }), 201
