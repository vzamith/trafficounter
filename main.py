import flet as ft
import os
import csv
import asyncio
from datetime import datetime

# --- CONFIGURAÇÃO GLOBAL ---
historico_total = []

# Classe Simples para gerenciar cada linha de contador
class GestorContador:
    def __init__(self, categoria, dd_ponto, dd_direcao, page):
        self.categoria = categoria
        self.dd_ponto = dd_ponto
        self.dd_direcao = dd_direcao
        self.valor = 0
        self.page = page

        # Criando os componentes visuais
        self.txt_valor = ft.Text(value="0", size=20, weight="bold", width=50, text_align="center")
        
        btn_menos = ft.ElevatedButton(
            text="-", 
            bgcolor="red", 
            color="white",
            on_click=self.diminuir
        )
        
        btn_mais = ft.ElevatedButton(
            text="+", 
            bgcolor="green", 
            color="white",
            on_click=self.aumentar
        )
        
        lbl_nome = ft.Text(value=categoria, width=150, size=16)

        # O Layout visual desta linha
        self.layout = ft.Row(
            controls=[lbl_nome, btn_menos, self.txt_valor, btn_mais],
            alignment="spaceBetween"
        )

    def atualizar_tela(self):
        self.txt_valor.value = str(self.valor)
        self.txt_valor.update()

    def registrar(self, delta):
        agora = datetime.now()
        acao = "Soma" if delta > 0 else "Subtracao"
        
        # Pega o valor dos Dropdowns (se estiver vazio, coloca um traço "-")
        ponto = self.dd_ponto.value if self.dd_ponto.value else "-"
        direcao = self.dd_direcao.value if self.dd_direcao.value else "-"

        # Adiciona ao histórico com as chaves corretas
        historico_total.append({
            "Data": agora.strftime("%Y-%m-%d"),
            "Hora": agora.strftime("%H:%M:%S"),
            "Ponto": ponto,
            "Direcao": direcao,  # Aqui garantimos que entra no CSV
            "Veiculo": self.categoria,
            "Acao": acao,
            "Total_Momento": self.valor
        })

    def aumentar(self, e):
        self.valor += 1
        self.registrar(1)
        self.atualizar_tela()

    def diminuir(self, e):
        if self.valor > 0:
            self.valor -= 1
            self.registrar(-1)
            self.atualizar_tela()


async def main(page: ft.Page):
    page.title = "DUSHANBE Traffic Survey"
    page.scroll = "auto"
    page.padding = 20
    page.theme_mode = "light"

    # --- CABEÇALHO (PONTO E DIREÇÃO) ---
    opcoes_ponto = [ft.dropdown.Option(str(i).zfill(2)) for i in range(1, 24)]
    
    dd_ponto = ft.Dropdown(
        label="Пункт (Point)",
        options=opcoes_ponto,
        width=150,
        hint_text="01-23"
    )

    dd_direcao = ft.Dropdown(
        label="Направление", # Label na tela DIRECTION
        options=[
            ft.dropdown.Option("A"), 
            ft.dropdown.Option("B")
        ],
        width=150,
        hint_text="A / B"
    )

    linha_config = ft.Row(
        controls=[dd_ponto, dd_direcao], 
        alignment="center"
    )

    # --- EXPORTAR CSV ---
    async def acao_exportar(e):
        btn = e.control
        if not historico_total:
            btn.text = "NO DATA"
            btn.bgcolor = "grey"
            btn.update()
            await asyncio.sleep(2)
            btn.text = "Экспорт данных" #EXPORTAR DADOS
            btn.bgcolor = "blue"
            btn.update()
            return

        # Define onde salvar
        nome_base = "survey_dushanbe"
        pasta = "/storage/emulated/0/Download"
        if not os.path.exists(pasta):
            pasta = "." 
            
        caminho = os.path.join(pasta, f"{nome_base}.csv")
        
        # Numera o arquivo se já existir (ex: survey_dushanbe_1.csv)
        count = 1
        while os.path.exists(caminho):
            caminho = os.path.join(pasta, f"{nome_base}_{count}.csv")
            count += 1

        try:
            with open(caminho, mode='w', newline='', encoding='utf-8') as f:
                # AQUI ESTÃO AS COLUNAS DO ARQUIVO FINAL
                cabecalho = ["Data", "Hora", "Ponto", "Direcao", "Veiculo", "Acao", "Total_Momento"]
                
                writer = csv.DictWriter(f, fieldnames=cabecalho)
                writer.writeheader()
                writer.writerows(historico_total)
            
            btn.text = f"SALVO: {os.path.basename(caminho)}"
            btn.bgcolor = "amber"
            btn.update()
        except Exception as ex:
            btn.text = "ERRO (Permissao)"
            btn.bgcolor = "red"
            print(ex)
            btn.update()

        await asyncio.sleep(2)
        btn.text = "Экспорт данных" #EXPORTAR DADOS
        btn.bgcolor = "blue"
        btn.update()

    # --- MONTAGEM DA TELA ---
    categorias = ["Автомобиль", "Такси", "Автобус", "Троллейбус", "Фургон / микроавтобус", "Мотоцикл", "Грузовик"] #["Carro", "Taxi", "Onibus", "Trolleybus", "Van/Minibus", "Moto", "Caminhao"]
    coluna_contadores = ft.Column(spacing=15)

    # Cria cada linha passando os dropdowns
    for cat in categorias:
        gestor = GestorContador(cat, dd_ponto, dd_direcao, page)
        coluna_contadores.controls.append(gestor.layout)

    btn_exportar = ft.ElevatedButton(
        text="Экспорт данных", #EXPORTAR DADOS
        height=60,
        bgcolor="blue",
        color="white",
        on_click=acao_exportar
    )

    # Adiciona tudo na página
    page.add(
        ft.Text("DUSHANBE Traffic Count", size=24, weight="bold"),
        ft.Divider(),
        ft.Text("Points:", weight="bold"),
        linha_config,
        ft.Divider(),
        coluna_contadores,
        ft.Divider(),
        ft.Container(content=btn_exportar, padding=20)
    )

ft.app(target=main)
