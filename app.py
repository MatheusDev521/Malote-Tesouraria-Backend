from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from PyPDF2 import PdfReader, PdfWriter
import io
import os
import traceback

app = Flask(__name__)

# 🔥 PERMITIR SEU FRONTEND DO GITHUB
CORS(app, resources={
    r"/*": {
        "origins": ["https://matheusdev521.github.io"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# ======= ROTA DE TESTE (muito importante para Render) =======
@app.route("/")
def home():
    return "Backend do Malote está ONLINE no Render 🚀"

# ======= ROTA DE HEALTH CHECK =======
@app.route("/health")
def health():
    return jsonify({"status": "ok", "message": "Backend funcionando"}), 200

# ======= ROTA PRINCIPAL =======
@app.route("/preencher-malote", methods=["POST", "OPTIONS"])
def preencher_malote_api():

    # Permitir preflight do CORS
    if request.method == "OPTIONS":
        return "", 204

    try:
        # 🔹 Verificar se recebeu dados
        if not request.json:
            return jsonify({"erro": "Nenhum dado recebido"}), 400

        dados = request.json
        print(f"📥 Dados recebidos: {dados}")

        # 🔹 Caminho seguro do PDF dentro do Render
        pdf_path = os.path.join(os.path.dirname(__file__), "malote.pdf")
        print(f"📂 Procurando PDF em: {pdf_path}")

        if not os.path.exists(pdf_path):
            print(f"❌ PDF não encontrado em: {pdf_path}")
            print(f"📁 Arquivos no diretório: {os.listdir(os.path.dirname(__file__))}")
            return jsonify({"erro": "Arquivo malote.pdf não encontrado no servidor!"}), 500

        print("✅ PDF encontrado, processando...")

        reader = PdfReader(pdf_path)
        writer = PdfWriter()

        for page in reader.pages:
            writer.add_page(page)

        # 🔹 Obter campos do PDF
        fields = writer.get_fields()
        
        if fields:
            print(f"📋 Campos disponíveis no PDF: {list(fields.keys())}")
        else:
            print("⚠️ Nenhum campo encontrado no PDF")

        # 🔹 Preencher campos
        campos_preenchidos = 0
        for campo, valor in dados.items():
            if fields and campo in fields:
                writer.update_page_form_field_values(writer.pages[0], {campo: str(valor)})
                campos_preenchidos += 1
                print(f"✏️ Preenchido: {campo} = {valor}")

        print(f"✅ Total de campos preenchidos: {campos_preenchidos}")

        # 🔹 Achatar o PDF
        for page in writer.pages:
            page.compress_content_streams()
            if "/Annots" in page:
                page["/Annots"] = []

        # 🔹 Gerar PDF em memória (não no disco)
        output = io.BytesIO()
        writer.write(output)
        output.seek(0)

        print("✅ PDF gerado com sucesso!")

        return send_file(
            output,
            mimetype="application/pdf",
            as_attachment=True,
            download_name="malote_preenchido.pdf"
        )

    except Exception as e:
        # 🔥 Capturar e retornar erro detalhado
        erro_detalhado = traceback.format_exc()
        print(f"❌ ERRO: {str(e)}")
        print(f"📋 Traceback completo:\n{erro_detalhado}")
        
        return jsonify({
            "erro": str(e),
            "detalhes": erro_detalhado
        }), 500

if __name__ == "__main__":
    # 🔥 CONFIGURAÇÃO PARA O RENDER
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
    
# ======= FIM DO CÓDIGO ======= #