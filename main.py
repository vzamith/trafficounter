import flet as ft
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

        # Componentes visuais
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

        self.layout = ft.Row(
            controls=[lbl_nome, btn_menos, self.txt_valor, btn_mais],
            alignment="spaceBetween"
        )

    def atualizar_tela(self):
        self.txt_valor.value = str(self.valor)
        self.txt_valor.update()

    async def efeito_flash(self):
        cor_original = self.page.bgcolor
        # Pisca cinza escuro (Hex code seguro)
        self.page.bgcolor = "#455A64" 
        self.page.update()
        await asyncio.sleep(0.1)
        self.page.bgcolor = cor_original
        self.page.update()

    def registrar(self, delta):
        agora = datetime.now()
        acao = "Soma" if delta > 0 else "Subtracao"
        
        ponto = self.dd_ponto.value if self.dd_ponto.value else "-"
        direcao = self.dd_direcao.value if self.dd_direcao.value else "-"

        historico_total.append({
            "Data": agora.strftime("%Y-%m-%d"),
            "Hora": agora.strftime("%H:%M:%S"),
            "Ponto": ponto,
            "Direcao": direcao,
            "Veiculo": self.categoria,
            "Acao": acao,
            "Total_Momento": self.valor
        })

    async def aumentar(self, e):
        self.valor += 1
        self.registrar(1)
        self.atualizar_tela()
        await self.efeito_flash() 

    async def diminuir(self, e):
        if self.valor > 0:
            self.valor -= 1
            self.registrar(-1)
            self.atualizar_tela()
            await self.efeito_flash()


async def main(page: ft.Page):
    page.title = "DUSHANBE Traffic Survey"
    page.scroll = "auto"
    page.padding = 20
    page.theme_mode = "light" 

    # --- 1. CONFIGURA O SELETOR DE ARQUIVOS (FILE PICKER) ---
    def salvar_arquivo_resultado(e: ft.FilePickerResultEvent):
        # Se o usuário cancelar a escolha da pasta, não faz nada
        if not e.path:
            return

        try:
            # Salva no caminho que o usuário escolheu (e.path)
            with open(e.path, mode='w', newline='', encoding='utf-8') as f:
                cabecalho = ["Data", "Hora", "Ponto", "Direcao", "Veiculo", "Acao", "Total_Momento"]
                writer = csv.DictWriter(f, fieldnames=cabecalho)
                writer.writeheader()
                writer.writerows(historico_total)
            
            # --- 2. POP UP SIMPLES "SAVED" ---
            dlg_saved = ft.AlertDialog(
                title=ft.Text("Saved"),
                content=None, 
                actions=[
                    ft.TextButton("OK", on_click=lambda _: page.close_dialog())
                ],
                actions_alignment="end",
            )
            page.dialog = dlg_saved
            dlg_saved.open = True
            page.update()

        except Exception as ex:
            dlg_erro = ft.AlertDialog(
                title=ft.Text("Error"),
                content=ft.Text(f"{ex}")
            )
            page.dialog = dlg_erro
            dlg_erro.open = True
            page.update()

    # Adiciona o componente invisível que abre a janela de arquivos
    file_picker = ft.FilePicker(on_result=salvar_arquivo_resultado)
    page.overlay.append(file_picker)
    page.update()

    # --- CABEÇALHO ---
    opcoes_ponto = [ft.dropdown.Option(str(i).zfill(2)) for i in range(1, 24)]
    
    dd_ponto = ft.Dropdown(
        label="Пункт (Point)",
        options=opcoes_ponto,
        width=150,
        hint_text="01-23"
    )

    dd_direcao = ft.Dropdown(
        label="Направление",
        options=[
            ft.dropdown.Option("A"), 
            ft.dropdown.Option("B")
        ],
        width=150,
        hint_text="A / B"
    )

    linha_config = ft.Row(controls=[dd_ponto, dd_direcao], alignment="center")

    # --- BOTÃO DE EXPORTAR ---
    def clicar_exportar(e):
        if not historico_total:
            dlg_aviso = ft.AlertDialog(title=ft.Text("No Data"))
            page.dialog = dlg_aviso
            dlg_aviso.open = True
            page.update()
            return
        
        # Gera um nome sugerido com Hora/Minuto
        nome_sugestao = f"survey_dushanbe_{datetime.now().strftime('%H-%M')}.csv"
        
        # AQUI ACONTECE A MÁGICA: Abre a janela pro usuário escolher a pasta
        file_picker.save_file(file_name=nome_sugestao)

    # --- MONTAGEM DA TELA ---
    categorias = ["Автомобиль (Car)", "Такси (Taxi)", "Автобус (Bus)", "Троллейбус (Trolley)", "микроавтобус(Minibus)", "Мотоцикл (Moto)", "Грузовик (Truck)"] 
    coluna_contadores = ft.Column(spacing=15)

    for cat in categorias:
        gestor = GestorContador(cat, dd_ponto, dd_direcao, page)
        coluna_contadores.controls.append(gestor.layout)

    btn_exportar = ft.ElevatedButton(
        text="Экспорт данных", 
        height=60,
        bgcolor="blue",
        color="white",
        on_click=clicar_exportar
    )

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
