from flask import Blueprint, jsonify, request
from mysql.connector.errors import IntegrityError

from db import get_cursor

categorias_bp = Blueprint('categorias', __name__)


@categorias_bp.route('/api/categorias', methods=['GET'])
def listar_categorias():
    tipo = request.args.get('tipo') 

    with get_cursor(dictionary=True) as cursor:
        if tipo:
            cursor.execute("SELECT * FROM categorias WHERE tipo = %s ORDER BY nome", (tipo,))
        else:
            cursor.execute("SELECT * FROM categorias ORDER BY nome")
        categorias = cursor.fetchall()

    return jsonify(categorias)


@categorias_bp.route('/api/categorias', methods=['POST'])
def criar_categoria():
    dados = request.get_json(silent=True) or {}

    nome = dados.get('nome')
    tipo = dados.get('tipo')
    cor = dados.get('cor', '#3B82F6')

    if not nome or tipo not in ('entrada', 'saida'):
        return jsonify({"erro": "Campos 'nome' e 'tipo' (entrada/saida) são obrigatórios"}), 400

    with get_cursor(commit=True) as cursor:
        cursor.execute(
            "INSERT INTO categorias (nome, tipo, cor) VALUES (%s, %s, %s)",
            (nome, tipo, cor)
        )
        nova_id = cursor.lastrowid

    return jsonify({"id": nova_id, "nome": nome, "tipo": tipo, "cor": cor}), 201


@categorias_bp.route('/api/categorias/<int:categoria_id>', methods=['DELETE'])
def deletar_categoria(categoria_id):
    try:
        with get_cursor(commit=True) as cursor:
            cursor.execute("DELETE FROM categorias WHERE id = %s", (categoria_id,))
            afetadas = cursor.rowcount
    except IntegrityError:
        return jsonify({
            "erro": "Essa categoria tem transações vinculadas e não pode ser excluída. "
                    "Exclua ou reatribua as transações dela antes de remover a categoria."
        }), 409

    if afetadas == 0:
        return jsonify({"erro": "Categoria não encontrada"}), 404
    return jsonify({"mensagem": "Categoria removida com sucesso"})
