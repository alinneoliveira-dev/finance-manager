from flask import Blueprint, jsonify, request
from datetime import datetime

from db import get_cursor

limites_bp = Blueprint('limites', __name__)


@limites_bp.route('/api/limites', methods=['GET'])
def listar_limites():
    mes_referencia = request.args.get('mes', datetime.now().strftime('%Y-%m'))

    with get_cursor(dictionary=True) as cursor:
        cursor.execute("""
            SELECT
                c.id AS categoria_id,
                c.nome AS categoria_nome,
                c.cor AS categoria_cor,
                l.limite_mensal,
                COALESCE((
                    SELECT SUM(t.valor)
                    FROM transacoes t
                    WHERE t.categoria_id = c.id
                      AND t.tipo = 'saida'
                      AND DATE_FORMAT(t.data_transacao, '%Y-%m') = %s
                ), 0) AS gasto_atual
            FROM categorias c
            LEFT JOIN limites_categoria l ON l.categoria_id = c.id
            WHERE c.tipo = 'saida'
            ORDER BY c.nome
        """, (mes_referencia,))
        resultado = cursor.fetchall()

    limites = []
    for row in resultado:
        limite = float(row['limite_mensal']) if row['limite_mensal'] is not None else None
        gasto = float(row['gasto_atual'])
        percentual = round((gasto / limite) * 100, 1) if limite and limite > 0 else None

        limites.append({
            "categoria_id": row['categoria_id'],
            "categoria_nome": row['categoria_nome'],
            "categoria_cor": row['categoria_cor'],
            "limite_mensal": limite,
            "gasto_atual": round(gasto, 2),
            "percentual": percentual
        })

    return jsonify({"mes_referencia": mes_referencia, "limites": limites})


@limites_bp.route('/api/limites', methods=['POST'])
def salvar_limite():
    dados = request.get_json(silent=True) or {}

    categoria_id = dados.get('categoria_id')
    limite_mensal = dados.get('limite_mensal')

    if not categoria_id or limite_mensal is None:
        return jsonify({"erro": "Campos obrigatórios: categoria_id, limite_mensal"}), 400

    with get_cursor(commit=True) as cursor:
        cursor.execute("""
            INSERT INTO limites_categoria (categoria_id, limite_mensal)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE limite_mensal = VALUES(limite_mensal)
        """, (categoria_id, limite_mensal))

    return jsonify({"mensagem": "Limite salvo com sucesso"}), 200
