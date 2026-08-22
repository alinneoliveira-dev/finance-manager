from flask import Blueprint, jsonify, request
from datetime import datetime

from db import get_connection

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    mes_referencia = request.args.get('mes', datetime.now().strftime('%Y-%m'))
    
    try:
        ano, mes = map(int, mes_referencia.split('-'))
    except ValueError:
        return jsonify({"erro": "Formato de mês inválido. Use YYYY-MM"}), 400

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            COALESCE(SUM(CASE WHEN tipo = 'entrada' THEN valor ELSE 0 END), 0) AS total_entradas,
            COALESCE(SUM(CASE WHEN tipo = 'saida' THEN valor ELSE 0 END), 0) AS total_saidas
        FROM transacoes 
        WHERE YEAR(data_transacao) = %s AND MONTH(data_transacao) = %s
    """, (ano, mes))

    resultado = cursor.fetchone()
    cursor.close()
    conn.close()

    total_entradas = float(resultado['total_entradas']) if resultado and resultado['total_entradas'] is not None else 0.0
    total_saidas = float(resultado['total_saidas']) if resultado and resultado['total_saidas'] is not None else 0.0
    saldo = total_entradas - total_saidas

    return jsonify({
        "mes_referencia": mes_referencia,
        "saldo_atual": round(saldo, 2),
        "total_entradas": round(total_entradas, 2),
        "total_saidas": round(total_saidas, 2)
    })