from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import NameObject, BooleanObject
import io
import os
import traceback

app = Flask(__name__)

# ===========================
# CORS (permitindo seu GitHub Pages)
# ===========================
CORS(app, resources={
    r"/*": {
        "origins": ["https://matheusdev521.github.io"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# ===========================
# ROTAS DE TESTE
# ===========================
@app.route("/")
def home():
    return "Backend do Malote está ONLINE no Render 🚀"

@app.route("/health")
def health():
    return jsonify({"status": "ok", "message": "Backend funcionando"}), 200

# ===========================
# ROTA PRINCIPAL
# ===========================
@app.route("/preencher-malote", methods=["POST", "OPTIONS"])
def preencher_malote_api():

    # Preflight CORS
    if request.method == "OPTIONS":
        return "", 204

    try:
        # Verifica se recebeu JSON
        if not request.json:
            return jsonify({"erro": "Nenhum dado recebido"}), 400

        dados = request.json
        print(f"\n📥 DADOS RECEBIDOS DO FRONTEND:\n{dados}\n")

        # Caminho do PDF dentro do Render
        pdf_path = os.path.join(os.path.dirname(__file__), "malote.pdf")
        print(f"📂 Procurando PDF em: {pdf_path}")

        if not os.path.exists(pdf_path):
            print("❌ PDF NÃO ENCONTRADO!")
            print("📁 Arquivos no diretório:", os.listdir(os.path.dirname(__file__)))
            return jsonify({"erro": "Arquivo malote.pdf não encontrado no servidor!"}), 500

        print("✅ PDF encontrado!")

        # Ler PDF original
        reader = PdfReader(pdf_path)
        writer = PdfWriter()

        print(f"📄 PDF possui {len(reader.pages)} página(s)")

        # 🔍 Mostrar campos reais do PDF (muito importante)
        campos_pdf = reader.get_fields()
        print("\n📋 CAMPOS EXISTENTES NO PDF:")
        print(campos_pdf)
        print("\n")

        # Copiar páginas para o writer
        for page in reader.pages:
            writer.add_page(page)

        # 🔹 FORÇAR RENDERIZAÇÃO VISUAL DOS CAMPOS (CORREÇÃO DO BRANCO)
        writer._root_object.update({
            NameObject("/NeedAppearances"): BooleanObject(True)
        })

        # Preencher campos em todas as páginas
        campos_preenchidos = 0

        for page_num in range(len(writer.pages)):
            writer.update_page_form_field_values(
                writer.pages[page_num],
                {campo: str(valor) for campo, valor in dados.items()}
            )
            campos_preenchidos += len(dados)

        print(f"✅ Campos processados: {campos_preenchidos}")

        # Gerar PDF em memória (sem salvar no servidor)
        output = io.BytesIO()
        writer.write(output)
        output.seek(0)

        print("✅ PDF gerado com sucesso e enviado ao frontend!")

        return send_file(
            output,
            mimetype="application/pdf",
            as_attachment=True,
            download_name="malote_preenchido.pdf"
        )

    except Exception as e:
        erro_detalhado = traceback.format_exc()
        print("\n❌ ERRO NO BACKEND:")
        print(erro_detalhado)

        return jsonify({
            "erro": str(e),
            "detalhes": erro_detalhado
        }), 500

# ===========================
# INICIALIZAÇÃO (Render)
# ===========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
