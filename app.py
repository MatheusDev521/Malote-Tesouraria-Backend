from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io, os, traceback
from datetime import datetime

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

def desenhar_checkbox(c, x, y, marcado=False, tamanho=0.4*cm):
    """Desenha um checkbox no PDF"""
    # Desenha o quadrado
    c.rect(x, y, tamanho, tamanho)
    
    # Se marcado, desenha um X
    if marcado:
        c.line(x, y, x + tamanho, y + tamanho)
        c.line(x + tamanho, y, x, y + tamanho)

@app.route("/preencher-malote", methods=["POST", "OPTIONS"])
def preencher_malote_api():
    if request.method == "OPTIONS":
        return "", 204

    try:
        dados = request.json
        if not dados:
            return jsonify({"erro": "Nenhum dado recebido"}), 400

        print("\n📥 DADOS RECEBIDOS:", dados)

        # Criar PDF em memória
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        # Configurações
        margem_esq = 2*cm
        y_atual = height - 3*cm

        # TÍTULO
        c.setFont("Helvetica-Bold", 16)
        c.drawString(margem_esq, y_atual, "PROTOCOLO DE ENTREGA DE MALOTE - TESOURARIA")
        y_atual -= 1.5*cm

        # DADOS DO REMETENTE
        c.setFont("Helvetica-Bold", 11)
        c.drawString(margem_esq, y_atual, "REMETENTE:")
        c.setFont("Helvetica", 11)
        c.drawString(margem_esq + 3*cm, y_atual, dados.get("REMETENTE", ""))
        
        y_atual -= 0.8*cm
        c.setFont("Helvetica-Bold", 11)
        c.drawString(margem_esq, y_atual, "Nº LACRE:")
        c.setFont("Helvetica", 11)
        c.drawString(margem_esq + 3*cm, y_atual, dados.get("N LACRE", ""))
        
        y_atual -= 1.2*cm

        # CABEÇALHO DA TABELA
        c.setFont("Helvetica-Bold", 10)
        
        # Posições das colunas
        col_num = margem_esq
        col_atendimento = margem_esq + 1*cm
        col_valor = margem_esq + 5*cm
        col_cartao = margem_esq + 10*cm
        col_especie = margem_esq + 13*cm
        
        # Desenhar linha de cabeçalho
        c.line(margem_esq, y_atual + 0.2*cm, width - margem_esq, y_atual + 0.2*cm)
        
        c.drawString(col_num, y_atual, "#")
        c.drawString(col_atendimento, y_atual, "ATENDIMENTO")
        c.drawString(col_valor, y_atual, "VALOR")
        c.drawString(col_cartao, y_atual, "CARTÃO")
        c.drawString(col_especie, y_atual, "ESPÉCIE")
        
        y_atual -= 0.6*cm
        c.line(margem_esq, y_atual + 0.2*cm, width - margem_esq, y_atual + 0.2*cm)
        y_atual -= 0.3*cm

        # ATENDIMENTOS
        c.setFont("Helvetica", 10)
        
        for i in range(1, 19):  # Até 18 atendimentos
            atendimento_key = f"ATENDIMENTORow{i}"
            valor_key = f"VALORRow{i}"
            
            if atendimento_key in dados:
                # Número da linha
                c.drawString(col_num, y_atual, str(i))
                
                # Número do atendimento
                c.drawString(col_atendimento, y_atual, dados.get(atendimento_key, ""))
                
                # Valor
                c.drawString(col_valor, y_atual, dados.get(valor_key, ""))
                
                # Checkboxes
                checkbox_cartao_num = i * 2 - 1
                checkbox_especie_num = i * 2
                
                cartao_marcado = dados.get(f"Check Box{checkbox_cartao_num}") == "On"
                especie_marcado = dados.get(f"Check Box{checkbox_especie_num}") == "On"
                
                desenhar_checkbox(c, col_cartao + 0.5*cm, y_atual - 0.1*cm, cartao_marcado)
                desenhar_checkbox(c, col_especie + 0.5*cm, y_atual - 0.1*cm, especie_marcado)
                
                y_atual -= 0.7*cm
                
                # Verificar se precisa de nova página
                if y_atual < 4*cm and i < 18:
                    c.showPage()
                    y_atual = height - 3*cm
                    
                    # Repetir cabeçalho na nova página
                    c.setFont("Helvetica-Bold", 10)
                    c.drawString(col_num, y_atual, "#")
                    c.drawString(col_atendimento, y_atual, "ATENDIMENTO")
                    c.drawString(col_valor, y_atual, "VALOR")
                    c.drawString(col_cartao, y_atual, "CARTÃO")
                    c.drawString(col_especie, y_atual, "ESPÉCIE")
                    y_atual -= 0.8*cm
                    c.setFont("Helvetica", 10)

        # Preencher linhas vazias até 18
        num_preenchidos = sum(1 for i in range(1, 19) if f"ATENDIMENTORow{i}" in dados)
        for i in range(num_preenchidos + 1, 19):
            if y_atual < 4*cm:
                break
            
            c.drawString(col_num, y_atual, str(i))
            desenhar_checkbox(c, col_cartao + 0.5*cm, y_atual - 0.1*cm, False)
            desenhar_checkbox(c, col_especie + 0.5*cm, y_atual - 0.1*cm, False)
            y_atual -= 0.7*cm

        # OBSERVAÇÕES
        y_atual -= 0.5*cm
        c.setFont("Helvetica-Bold", 11)
        c.drawString(margem_esq, y_atual, "OBS:")
        
        y_atual -= 0.6*cm
        c.setFont("Helvetica", 10)
        
        observacao = dados.get("OBS:", "")
        if observacao:
            # Quebrar texto em linhas se necessário
            max_chars = 85
            palavras = observacao.split()
            linha_atual = ""
            
            for palavra in palavras:
                if len(linha_atual + " " + palavra) <= max_chars:
                    linha_atual += (" " + palavra if linha_atual else palavra)
                else:
                    c.drawString(margem_esq, y_atual, linha_atual)
                    y_atual -= 0.5*cm
                    linha_atual = palavra
            
            if linha_atual:
                c.drawString(margem_esq, y_atual, linha_atual)
                y_atual -= 0.5*cm

        # RODAPÉ
        y_atual -= 1*cm
        c.line(margem_esq, y_atual, margem_esq + 6*cm, y_atual)
        y_atual -= 0.5*cm
        c.setFont("Helvetica", 10)
        c.drawString(margem_esq, y_atual, "Recebido: ____________________")
        
        c.drawString(margem_esq + 10*cm, y_atual, f"Data: ___/___/_____")

        # Finalizar PDF
        c.save()
        buffer.seek(0)

        return send_file(
            buffer,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"malote_{dados.get('N LACRE', 'protocolo')}.pdf"
        )

    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)