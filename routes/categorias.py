from flask import Blueprint, jsonify, request

from db import get_connection

categorias_bp = Blueprint('categorias', __name__)


@categorias_bp.route('/api/categorias', methods=['GET'])
def listar_categorias():
    tipo = request.args.get('tipo')  

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if tipo:
        cursor.execute("SELECT * FROM categorias WHERE tipo = %s ORDER BY nome", (tipo,))
    else:
        cursor.execute("SELECT * FROM categorias ORDER BY nome")

    categorias = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify(categorias)


@categorias_bp.route('/api/categorias', methods=['POST'])
def criar_categoria():
    dados = request.get_json(silent=True) or {}

    nome = dados.get('nome')
    tipo = dados.get('tipo')
    cor = dados.get('cor', '#3B82F6')

    if not nome or tipo not in ('entrada', 'saida'):
        return jsonify({"erro": "Campos 'nome' e 'tipo' (entrada/saida) são obrigatórios"}), 400

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO categorias (nome, tipo, cor) VALUES (%s, %s, %s)",
        (nome, tipo, cor)
    )
    conn.commit()
    nova_id = cursor.lastrowid
    cursor.close()
    conn.close()

    return jsonify({"id": nova_id, "nome": nome, "tipo": tipo, "cor": cor}), 201


@categorias_bp.route('/api/categorias/<int:categoria_id>', methods=['DELETE'])
def deletar_categoria(categoria_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM categorias WHERE id = %s", (categoria_id,))
    conn.commit()
    afetadas = cursor.rowcount
    cursor.close()
    conn.close()

    if afetadas == 0:
        return jsonify({"erro": "Categoria não encontrada"}), 404
    return jsonify({"mensagem": "Categoria removida com sucesso"})
