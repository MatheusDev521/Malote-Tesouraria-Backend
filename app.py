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

        # 🔹 Ler o PDF original
        reader = PdfReader(pdf_path)
        writer = PdfWriter()

        # 🔹 Copiar todas as páginas
        for page in reader.pages:
            writer.add_page(page)

        print(f"📄 PDF tem {len(reader.pages)} página(s)")

        # 🔹 MÉTODO CORRETO PARA PREENCHER CAMPOS NO PYPDF2
        campos_preenchidos = 0
        
        # Para cada página, atualizar os campos
        for page_num in range(len(writer.pages)):
            # Criar dicionário com os campos para esta página
            campos_para_atualizar = {}
            
            for campo, valor in dados.items():
                # Converter valor para string
                campos_para_atualizar[campo] = str(valor)
            
            # Atualizar campos da página
            writer.update_page_form_field_values(
                writer.pages[page_num],
                campos_para_atualizar
            )
            campos_preenchidos += len(campos_para_atualizar)
        
        print(f"✅ Campos processados: {campos_preenchidos}")

        # 🔹 Achatar o PDF (remover campos editáveis)
        for page in writer.pages:
            if "/Annots" in page:
                del page["/Annots"]
            if "/AcroForm" in page:
                del page["/AcroForm"]

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