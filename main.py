import os
import csv
from datetime import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.utils import get_color_from_hex
from kivy.clock import Clock

class ContadorApp(App):
    def build(self):
        self.categorias = ["Carro", "Taxi", "Onibus", "Trolleybus", "Van (Minibus)", "Motorcycle", "Trucks"]
        self.contagens = {cat: 0 for cat in self.categorias}
        
        # O histórico NUNCA é limpo durante a execução
        self.historico_total = []
        
        root = BoxLayout(orientation='vertical', padding=10, spacing=10)
        root.add_widget(Label(text="DUSHANBE OD Survey - Registro Contínuo", font_size='18sp', size_hint_y=None, height=50))
        
        scroll = ScrollView()
        lista_itens = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10)
        lista_itens.bind(minimum_height=lista_itens.setter('height'))
        
        self.labels_valores = {}

        for cat in self.categorias:
            item_frame = BoxLayout(size_hint_y=None, height=80, spacing=10)
            lbl_nome = Label(text=cat, halign='left', text_size=(250, None))
            
            btn_menos = Button(text='-', size_hint_x=None, width=100, background_color=get_color_from_hex('#E74C3C'))
            btn_menos.bind(on_release=lambda btn, c=cat: self.registrar_clique(c, -1))
            
            lbl_val = Label(text='0', font_size='20sp', bold=True, size_hint_x=None, width=60)
            self.labels_valores[cat] = lbl_val
            
            btn_mais = Button(text='+', size_hint_x=None, width=100, background_color=get_color_from_hex('#2ECC71'))
            btn_mais.bind(on_release=lambda btn, c=cat: self.registrar_clique(c, 1))
            
            item_frame.add_widget(lbl_nome)
            item_frame.add_widget(btn_menos)
            item_frame.add_widget(lbl_val)
            item_frame.add_widget(btn_mais)
            lista_itens.add_widget(item_frame)
        
        scroll.add_widget(lista_itens)
        root.add_widget(scroll)
        
        self.btn_exportar = Button(text="EXPORTAR CLIQUES (CSV)", size_hint_y=None, height=80, 
                                   background_color=get_color_from_hex('#3498DB'), bold=True)
        self.btn_exportar.bind(on_release=self.exportar_csv)
        root.add_widget(self.btn_exportar)
        
        return root

    def registrar_clique(self, veiculo, delta):
        if self.contagens[veiculo] + delta >= 0:
            self.contagens[veiculo] += delta
            self.labels_valores[veiculo].text = str(self.contagens[veiculo])
            
            agora = datetime.now()
            # Adiciona ao histórico total sem nunca remover
            self.historico_total.append({
                "Data": agora.strftime("%Y-%m-%d"),
                "Hora": agora.strftime("%H:%M:%S"),
                "Veiculo": veiculo,
                "Acao": "Soma" if delta > 0 else "Subtracao",
                "Total_Momento": self.contagens[veiculo]
            })

    def resetar_estilo_botao(self, *args):
        """Volta o botão ao texto e cor originais."""
        self.btn_exportar.text = "EXPORTAR CLIQUES (CSV)"
        self.btn_exportar.background_color = get_color_from_hex('#3498DB')

    def exportar_csv(self, instance):
        if not self.historico_total:
            instance.text = "SEM DADOS"
            Clock.schedule_once(self.resetar_estilo_botao, 2)
            return

        nome_base = "registro_od_dushanbe"
        extensao = ".csv"
        # Pasta de downloads no Android ou pasta local no PC
        pasta_destino = "/storage/emulated/0/Download" if os.path.exists("/storage/emulated/0/Download") else "."
        
        contador = 0
        nome_arquivo = f"{nome_base}{extensao}"
        caminho_completo = os.path.join(pasta_destino, nome_arquivo)

        # Lógica de nomes: registro.csv, registro_1.csv, registro_2.csv...
        while os.path.exists(caminho_completo):
            contador += 1
            nome_arquivo = f"{nome_base}_{contador}{extensao}"
            caminho_completo = os.path.join(pasta_destino, nome_arquivo)

        try:
            with open(caminho_completo, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=["Data", "Hora", "Veiculo", "Acao", "Total_Momento"])
                writer.writeheader()
                writer.writerows(self.historico_total)
            
            # Feedback visual de sucesso
            instance.text = f"SALVO: {nome_arquivo}"
            instance.background_color = get_color_from_hex('#F39C12')
            
            # Agenda o RESET do botão (apenas visual)
            Clock.schedule_once(self.resetar_estilo_botao, 2)
            
        except Exception as e:
            instance.text = "ERRO AO SALVAR"
            Clock.schedule_once(self.resetar_estilo_botao, 2)

if __name__ == '__main__':
    ContadorApp().run()