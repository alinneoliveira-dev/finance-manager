from flask import Blueprint, jsonify, request

from db import get_connection

transacoes_bp = Blueprint('transacoes', __name__)


@transacoes_bp.route('/api/transacoes', methods=['GET'])
def listar_transacoes():
    tipo = request.args.get('tipo')
    categoria_id = request.args.get('categoria_id')
    busca = request.args.get('busca')

    query = """
        SELECT tra.id, tra.descricao, tra.valor, tra.tipo, tra.data_transacao,
               cat.id AS categoria_id, cat.nome AS categoria_nome, cat.cor AS categoria_cor
        FROM transacoes tra
        LEFT JOIN categorias cat ON cat.id = tra.categoria_id
        WHERE 1=1
    """
    params = []

    if tipo:
        query += " AND tra.tipo = %s"
        params.append(tipo)

    if categoria_id:
        query += " AND tra.categoria_id = %s"
        params.append(categoria_id)

    if busca:
        query += " AND tra.descricao LIKE %s"
        params.append(f"%{busca}%")

    query += " ORDER BY tra.data_transacao DESC, tra.id DESC"

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, params)
    transacoes = cursor.fetchall()
    cursor.close()
    conn.close()

    for t in transacoes:
        t['valor'] = float(t['valor'])
        t['data_transacao'] = t['data_transacao'].strftime('%Y-%m-%d')

    return jsonify({"total": len(transacoes), "transacoes": transacoes})


@transacoes_bp.route('/api/transacoes', methods=['POST'])
def criar_transacao():
    dados = request.get_json(silent=True) or {}

    descricao = dados.get('descricao')
    valor = dados.get('valor')
    tipo = dados.get('tipo')
    categoria_id = dados.get('categoria_id')
    data_transacao = dados.get('data_transacao') 

    if not descricao or valor is None or tipo not in ('entrada', 'saida') or not data_transacao:
        return jsonify({
            "erro": "Campos obrigatórios: descricao, valor, tipo (entrada/saida), data_transacao"
        }), 400

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO transacoes (descricao, valor, tipo, categoria_id, data_transacao)
        VALUES (%s, %s, %s, %s, %s)
    """, (descricao, valor, tipo, categoria_id, data_transacao))
    conn.commit()
    nova_id = cursor.lastrowid
    cursor.close()
    conn.close()

    return jsonify({"id": nova_id, "mensagem": "Transação registrada com sucesso"}), 201


@transacoes_bp.route('/api/transacoes/<int:transacao_id>', methods=['DELETE'])
def deletar_transacao(transacao_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transacoes WHERE id = %s", (transacao_id,))
    conn.commit()
    afetadas = cursor.rowcount
    cursor.close()
    conn.close()

    if afetadas == 0:
        return jsonify({"erro": "Transação não encontrada"}), 404
    return jsonify({"mensagem": "Transação removida com sucesso"})
