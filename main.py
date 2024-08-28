import tkinter as tk
from tkinter import ttk

class Historico:
    def __init__(self, master):
        self.master = master
        self.master.title("Histórico")
        self.master.geometry("300x400")
        self.master.configure(bg='#2E2E2E')
        
        self.historico = []
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview", background="#2E2E2E", fieldbackground="#2E2E2E", foreground="white")
        style.configure("Treeview.Heading", background="#3E3E3E", foreground="white")

        self.tree = ttk.Treeview(master, columns=("Expressão", "Resultado"), show="headings")
        self.tree.heading("Expressão", text="Expressão")
        self.tree.heading("Resultado", text="Resultado")
        self.tree.column("Expressão", width=150)
        self.tree.column("Resultado", width=150)
        self.tree.pack(fill=tk.BOTH, expand=True)

    def adicionar(self, expressao, resultado):
        self.historico.append((expressao, resultado))
        self.tree.insert("", "end", values=(expressao, resultado))

    def limpar(self):
        self.historico.clear()
        for item in self.tree.get_children():
            self.tree.delete(item)

class Calculadora:
    def __init__(self, master):
        self.master = master
        master.title("Calculadora")
        master.geometry("250x320")
        master.configure(bg='#2E2E2E')

        self.total = 0
        self.entrada_atual = "0"
        self.operacao_pendente = None
        self.inicio_nova_entrada = True
        self.resultado_exibido = False
        
        self.historico_janela = None
        self.historico = Historico(tk.Toplevel(master))
        self.historico.master.withdraw()

        # Frame para o display de histórico e botão de histórico
        frame_historico = tk.Frame(master, bg='#2E2E2E')
        frame_historico.grid(row=0, column=0, columnspan=4, sticky='nsew', padx=5, pady=5)

        # Display de histórico
        self.display_historico = tk.Label(frame_historico, text="", font=('Arial', 12), anchor='e', bg='#3E3E3E', fg='white')
        self.display_historico.pack(side=tk.LEFT, expand=True, fill=tk.X)

        # Botão de histórico
        self.botao_historico = tk.Button(frame_historico, text="H", width=2, height=1, command=self.abrir_historico, bg='#4E4E4E', fg='white')
        self.botao_historico.pack(side=tk.RIGHT)

        # Display principal
        self.display = tk.Entry(master, width=20, font=('Arial', 16), justify='right', bg='#3E3E3E', fg='white', insertbackground='white')
        self.display.grid(row=1, column=0, columnspan=4, padx=5, pady=5)
        self.atualizar_display()

        # Botões
        botoes = [
            '%', 'CE', 'C', '/',
            '7', '8', '9', '*',
            '4', '5', '6', '-',
            '1', '2', '3', '+',
            '+/-', '0', ',', '='
        ]

        row = 2
        col = 0
        for botao in botoes:
            comando = lambda x=botao: self.click(x)
            tk.Button(master, text=botao, width=5, height=2, command=comando, 
                      bg='#4E4E4E', fg='white').grid(row=row, column=col, padx=1, pady=1, sticky='nsew')
            col += 1
            if col > 3:
                col = 0
                row += 1

        # Configurar o peso das linhas e colunas para permitir que os botões se expandam
        for i in range(2, 7):  # Linhas dos botões
            master.grid_rowconfigure(i, weight=1)
        for i in range(4):  # Colunas dos botões
            master.grid_columnconfigure(i, weight=1)

    def click(self, key):
        if key == '=':
            self.calcular()
            self.resultado_exibido = True
        elif key in '0123456789':
            if self.inicio_nova_entrada or self.entrada_atual == "0":
                self.entrada_atual = key
                self.inicio_nova_entrada = False
            else:
                self.entrada_atual += key
        elif key == ',':
            if ',' not in self.entrada_atual:
                self.entrada_atual += key
        elif key == '%':
            self.calcular_porcentagem()
        elif key == 'CE':
            self.entrada_atual = "0"
            self.inicio_nova_entrada = True
        elif key == 'C':
            self.limpar()
        elif key == '+/-':
            if self.entrada_atual != "0":
                if self.entrada_atual[0] == '-':
                    self.entrada_atual = self.entrada_atual[1:]
                else:
                    self.entrada_atual = '-' + self.entrada_atual
        else:  # Operadores
            if self.operacao_pendente and not self.inicio_nova_entrada:
                self.calcular()
            self.total = float(self.entrada_atual.replace(',', '.'))
            self.operacao_pendente = key
            self.inicio_nova_entrada = True
            self.atualizar_historico(self.formatar_numero(self.total) + " " + key)
        self.atualizar_display()

    def calcular(self):
        if self.operacao_pendente:
            atual = float(self.entrada_atual.replace(',', '.'))
            expressao = f"{self.formatar_numero(self.total)} {self.operacao_pendente} {self.formatar_numero(atual)}"
            if self.operacao_pendente == '+':
                self.total += atual
            elif self.operacao_pendente == '-':
                self.total -= atual
            elif self.operacao_pendente == '*':
                self.total *= atual
            elif self.operacao_pendente == '/':
                if atual != 0:
                    self.total /= atual
                else:
                    self.total = "Erro: Divisão por zero!"
            resultado = self.formatar_numero(self.total)
            self.entrada_atual = resultado
            self.operacao_pendente = None
            self.atualizar_historico(expressao + " =")
            self.historico.adicionar(expressao, resultado)
        self.inicio_nova_entrada = False

    def calcular_porcentagem(self):
        if self.operacao_pendente in ('+', '-'):
            percentagem = self.total * (float(self.entrada_atual.replace(',', '.')) / 100)
        else:
            percentagem = float(self.entrada_atual.replace(',', '.')) / 100
        self.entrada_atual = self.formatar_numero(percentagem)
        self.atualizar_display()

    def formatar_numero(self, numero):
        if isinstance(numero, str):
            return numero
        if numero.is_integer():
            return str(int(numero))
        return f"{numero:.10f}".rstrip('0').rstrip('.').replace('.', ',')

    def atualizar_display(self):
        self.display.delete(0, tk.END)
        self.display.insert(0, self.entrada_atual)

    def atualizar_historico(self, texto):
        self.display_historico.config(text=texto)

    def limpar(self):
        self.total = 0
        self.entrada_atual = "0"
        self.operacao_pendente = None
        self.inicio_nova_entrada = True
        self.resultado_exibido = False
        self.atualizar_display()
        self.atualizar_historico("")

    def abrir_historico(self):
        if self.historico_janela is None or not self.historico_janela.winfo_exists():
            self.historico_janela = self.historico.master
            self.historico_janela.deiconify()
        else:
            self.historico_janela.lift()

# Criar a janela principal
janela = tk.Tk()
calculadora = Calculadora(janela)
janela.mainloop()