from flask import Flask, request, send_file
from flask_cors import CORS
from PyPDF2 import PdfReader, PdfWriter
import io
import os

app = Flask(__name__)

# 🔥 PERMITIR SEU FRONTEND DO GITHUB
CORS(app, resources={
    r"/*": {
        "origins": ["https://matheusdev521.github.io"]
    }
})

# ======= ROTA DE TESTE (muito importante para Render) =======
@app.route("/")
def home():
    return "Backend do Malote está ONLINE no Render 🚀"

# ======= ROTA PRINCIPAL =======
@app.route("/preencher-malote", methods=["POST", "OPTIONS"])
def preencher_malote_api():

    # Permitir preflight do CORS
    if request.method == "OPTIONS":
        return "", 204

    dados = request.json

    # 🔹 Caminho seguro do PDF dentro do Render
    pdf_path = os.path.join(os.path.dirname(__file__), "malote.pdf")

    if not os.path.exists(pdf_path):
        return {"erro": "Arquivo malote.pdf não encontrado no servidor!"}, 500

    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    fields = writer.get_fields()

    for campo, valor in dados.items():
        if fields and campo in fields:
            writer.update_field(campo, valor)

    writer.flatten_pages()

    # 🔹 Gerar PDF em memória (não no disco)
    output = io.BytesIO()
    writer.write(output)
    output.seek(0)

    return send_file(
        output,
        mimetype="application/pdf",
        as_attachment=True,
        download_name="malote_preenchido.pdf"
    )

if __name__ == "__main__":
    app.run(debug=True)
    
# ======= FIM DO CÓDIGO ======= #