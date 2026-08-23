from flask import Blueprint, jsonify, request
from datetime import datetime

from db import get_cursor

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    mes_referencia = request.args.get('mes', datetime.now().strftime('%Y-%m'))

    with get_cursor(dictionary=True) as cursor:
        cursor.execute("""
            SELECT
                COALESCE(SUM(CASE WHEN tipo = 'entrada' THEN valor ELSE 0 END), 0) AS total_entradas,
                COALESCE(SUM(CASE WHEN tipo = 'saida' THEN valor ELSE 0 END), 0) AS total_saidas
            FROM transacoes
            WHERE DATE_FORMAT(data_transacao, '%Y-%m') = %s
        """, (mes_referencia,))
        resultado = cursor.fetchone()

    total_entradas = float(resultado['total_entradas'])
    total_saidas = float(resultado['total_saidas'])
    saldo = total_entradas - total_saidas

    return jsonify({
        "mes_referencia": mes_referencia,
        "saldo_atual": round(saldo, 2),
        "total_entradas": round(total_entradas, 2),
        "total_saidas": round(total_saidas, 2)
    })
