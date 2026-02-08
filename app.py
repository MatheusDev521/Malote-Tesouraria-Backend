from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from pypdf import PdfReader, PdfWriter
import io
import os

app = Flask(__name__)
CORS(app)  # Permite requisições do frontend

# Caminho do PDF template
PDF_TEMPLATE = "malote.pdf"

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint para verificar se o servidor está rodando"""
    return jsonify({"status": "online", "message": "Backend funcionando!"}), 200

@app.route('/preencher-malote', methods=['POST'])
def preencher_malote():
    try:
        # Receber os dados JSON do frontend
        dados = request.json
        
        if not dados:
            return jsonify({"erro": "Nenhum dado recebido"}), 400
        
        # Verificar se o arquivo PDF existe
        if not os.path.exists(PDF_TEMPLATE):
            return jsonify({"erro": "Arquivo PDF template não encontrado"}), 500
        
        # Ler o PDF template
        reader = PdfReader(PDF_TEMPLATE)
        writer = PdfWriter()
        writer.append(reader)
        
        # Preencher os campos com os dados recebidos
        writer.update_page_form_field_values(
            writer.pages[0],
            dados
        )
        
        # Salvar o PDF em memória (usando BytesIO)
        pdf_buffer = io.BytesIO()
        writer.write(pdf_buffer)
        pdf_buffer.seek(0)
        
        # Retornar o PDF gerado
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'malote_{dados.get("N_LACRE", "sem_lacre")}.pdf'
        )
        
    except Exception as e:
        print(f"Erro ao gerar PDF: {str(e)}")
        return jsonify({"erro": str(e)}), 500

if __name__ == '__main__':
    # Para produção no Render
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)