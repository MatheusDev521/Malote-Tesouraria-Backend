from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from PyPDF2 import PdfReader, PdfWriter
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

        # Verificar se existe o PDF template
        pdf_path = os.path.join(os.path.dirname(__file__), "malote.pdf")
        
        if not os.path.exists(pdf_path):
            return jsonify({"erro": "Arquivo malote.pdf não encontrado no servidor"}), 404

        # Criar overlay com os dados
        packet = io.BytesIO()
        c = canvas.Canvas(packet, pagesize=A4)
        width, height = A4

        # ======================================
        # POSIÇÕES AJUSTADAS PARA O PDF DE MALOTE
        # ======================================
        
        # Campos superiores (REMETENTE e Nº LACRE)
        # Baseado na estrutura típica do formulário
        x_remetente = 3.8*cm      # Após "REMETENTE:"
        y_remetente = height - 3.5*cm
        
        x_lacre = 3.3*cm          # Após "Nº LACRE:"
        y_lacre = height - 4.2*cm
        
        # Tabela de atendimentos
        # Começa após o cabeçalho da tabela
        y_primeira_linha = height - 6.2*cm
        espaco_entre_linhas = 0.85*cm
        
        # Colunas da tabela
        x_atendimento = 1.8*cm    # Coluna ATENDIMENTO
        x_valor = 5.8*cm          # Coluna VALOR
        x_checkbox_cartao = 10.8*cm   # Checkbox CARTÃO
        x_checkbox_especie = 14.2*cm  # Checkbox ESPÉCIE
        
        # Campo de observação
        x_obs = 1.5*cm
        y_obs = 4.8*cm
        
        # ======================================
        # PREENCHER DADOS
        # ======================================
        
        # REMETENTE
        c.setFont("Helvetica", 11)
        c.drawString(x_remetente, y_remetente, dados.get("REMETENTE", ""))
        
        # Nº LACRE
        c.drawString(x_lacre, y_lacre, dados.get("N LACRE", ""))
        
        # ATENDIMENTOS
        c.setFont("Helvetica", 10)
        
        for i in range(1, 19):  # Até 18 atendimentos
            atendimento_key = f"ATENDIMENTORow{i}"
            valor_key = f"VALORRow{i}"
            
            # Calcular posição Y desta linha
            y_linha = y_primeira_linha - ((i - 1) * espaco_entre_linhas)
            
            if atendimento_key in dados:
                # Número do atendimento
                c.drawString(x_atendimento, y_linha, dados.get(atendimento_key, ""))
                
                # Valor (remover "R$ " se já vier no dado)
                valor = dados.get(valor_key, "")
                c.drawString(x_valor, y_linha, valor)
                
                # Checkboxes - desenhar X quando marcado
                checkbox_cartao_num = i * 2 - 1
                checkbox_especie_num = i * 2
                
                cartao_marcado = dados.get(f"Check Box{checkbox_cartao_num}") == "On"
                especie_marcado = dados.get(f"Check Box{checkbox_especie_num}") == "On"
                
                c.setLineWidth(2.5)
                
                # X para CARTÃO
                if cartao_marcado:
                    # Ajustar posição do X dentro do parêntese
                    x_base = x_checkbox_cartao + 0.1*cm
                    y_base = y_linha - 0.05*cm
                    tamanho = 0.3*cm
                    
                    c.line(x_base, y_base, x_base + tamanho, y_base + tamanho)
                    c.line(x_base + tamanho, y_base, x_base, y_base + tamanho)
                
                # X para ESPÉCIE
                if especie_marcado:
                    x_base = x_checkbox_especie + 0.1*cm
                    y_base = y_linha - 0.05*cm
                    tamanho = 0.3*cm
                    
                    c.line(x_base, y_base, x_base + tamanho, y_base + tamanho)
                    c.line(x_base + tamanho, y_base, x_base, y_base + tamanho)
                
                c.setLineWidth(1)

        # OBSERVAÇÕES
        c.setFont("Helvetica", 9)
        observacao = dados.get("OBS:", "")
        
        if observacao:
            # Quebrar texto em múltiplas linhas se necessário
            max_chars = 85
            palavras = observacao.split()
            linha_atual = ""
            y_obs_atual = y_obs
            
            for palavra in palavras:
                teste = linha_atual + (" " + palavra if linha_atual else palavra)
                if len(teste) <= max_chars:
                    linha_atual = teste
                else:
                    if linha_atual:
                        c.drawString(x_obs, y_obs_atual, linha_atual)
                        y_obs_atual -= 0.4*cm
                    linha_atual = palavra
            
            # Última linha
            if linha_atual:
                c.drawString(x_obs, y_obs_atual, linha_atual)

        # Finalizar overlay
        c.save()
        packet.seek(0)

        # ======================================
        # MESCLAR COM PDF ORIGINAL
        # ======================================
        
        # Ler o PDF template
        template_pdf = PdfReader(pdf_path)
        overlay_pdf = PdfReader(packet)
        
        # Criar PDF de saída
        output = PdfWriter()
        
        # Mesclar overlay sobre o template
        page = template_pdf.pages[0]
        page.merge_page(overlay_pdf.pages[0])
        output.add_page(page)
        
        # Gerar arquivo final
        output_buffer = io.BytesIO()
        output.write(output_buffer)
        output_buffer.seek(0)

        print("✅ PDF gerado com sucesso!")

        return send_file(
            output_buffer,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"malote_{dados.get('N LACRE', 'protocolo')}.pdf"
        )

    except FileNotFoundError:
        return jsonify({"erro": "Arquivo malote.pdf não encontrado no servidor. Certifique-se de fazer upload do template."}), 404
    except Exception as e:
        print("❌ ERRO:", traceback.format_exc())
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
