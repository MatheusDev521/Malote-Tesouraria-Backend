from flask import Flask, request, send_file
from flask_cors import CORS
from PyPDF2 import PdfReader, PdfWriter

app = Flask(__name__)

# 🔥 PERMITIR SEU FRONTEND DO GITHUB
CORS(app, resources={
    r"/*": {
        "origins": ["https://matheusdev521.github.io"]
    }
})


@app.route("/preencher-malote", methods=["POST"])
def preencher_malote_api():
    dados = request.json

    # >>> O PDF em branco é carregado AUTOMATICAMENTE aqui <<<
    reader = PdfReader("malote.pdf")
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    fields = writer.get_fields()

    for campo, valor in dados.items():
        if campo in fields:
            writer.update_field(campo, valor)

    writer.flatten_pages()

    output = "malote_preenchido.pdf"
    with open(output, "wb") as f:
        writer.write(f)

    return send_file(output, as_attachment=True)

if __name__ == "__main__":
    app.run()
