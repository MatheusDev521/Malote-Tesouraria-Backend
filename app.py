from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import NameObject, BooleanObject
import io, os, traceback

app = Flask(__name__)

CORS(app, resources={
    r"/*": {
        "origins": ["https://matheusdev521.github.io"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

@app.route("/")
def home():
    return "Backend do Malote está ONLINE no Render 🚀"

@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200

@app.route("/preencher-malote", methods=["POST", "OPTIONS"])
def preencher_malote_api():

    if request.method == "OPTIONS":
        return "", 204

    try:
        dados = request.json
        if not dados:
            return jsonify({"erro": "Nenhum dado recebido"}), 400

        print("\n📥 DADOS RECEBIDOS:", dados)

        pdf_path = os.path.join(os.path.dirname(__file__), "malote.pdf")

        reader = PdfReader(pdf_path)
        writer = PdfWriter()

        for p in reader.pages:
            writer.add_page(p)

        # Forçar aparência dos campos no PDF
        writer._root_object.update({
            NameObject("/NeedAppearances"): BooleanObject(True)
        })

        page = writer.pages[0]

        # Corrigir formato das checkboxes para o padrão do PDF
        campos_corrigidos = {}
        for k, v in dados.items():
            if "Check Box" in k:
                campos_corrigidos[k] = True if v in ["On", "true", True] else False
            else:
                campos_corrigidos[k] = str(v)

        print("📌 Campos finais enviados ao PDF:", campos_corrigidos)

        writer.update_page_form_field_values(page, campos_corrigidos)

        output = io.BytesIO()
        writer.write(output)
        output.seek(0)

        return send_file(
            output,
            mimetype="application/pdf",
            as_attachment=True,
            download_name="malote_preenchido.pdf"
        )

    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
