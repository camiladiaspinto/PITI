import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
from threading import Thread
import serial
from datetime import datetime
from camada7 import send_data, receive_data, received_frames_queue, received_frames_queue_sender, reconstruct_file, split, frame_layer, send_data_receiver, receive_data_receiver

SERIAL_PORT_SENDER = 'COM3'
SERIAL_PORT_RECEIVER = 'COM4'

class InterfaceGrafica:
    def __init__(self, master):
        self.master = master
        master.title("PITI4")
        master.geometry("600x600")  # Define o tamanho da janela para 600x600

        self.label = ctk.CTkLabel(master, text="Selecione se deseja ser o emissor ou receptor:", font=("Arial", 14))
        self.label.pack(pady=10)

        self.emissor_button = ctk.CTkButton(master, text="Emissor", command=self.emissor_menu, width=200, fg_color='#6a93a9', text_color="white")
        self.emissor_button.pack(pady=5)

        self.recetor_button = ctk.CTkButton(master, text="Recetor", command=self.recetor_menu, width=200, fg_color='#6c9562', text_color="white")
        self.recetor_button.pack(pady=5)

        self.received_files_queue = received_frames_queue  # Fila para armazenar os arquivos recebidos

    def emissor_menu(self):
        self.label.configure(text="Menu do Emissor")
        self.emissor_button.pack_forget()
        self.recetor_button.pack_forget()
        self.create_text_box()

        global serial_port_e
        serial_port_e = serial.Serial(SERIAL_PORT_SENDER, 9600, timeout=2)

        self.enviar_button = ctk.CTkButton(self.master, text="Enviar Arquivo", command=lambda: self.enviar_arquivo(serial_port_e), fg_color='#6a93a9')
        self.enviar_button.pack(pady=5)

        self.text_entry_emissor = ctk.CTkEntry(self.master, width=400)  # Caixa de entrada de texto para o emissor
        self.text_entry_emissor.pack(pady=5)
        self.text_entry_emissor.insert(0, "Escreva a sua mensagem...")
        self.text_entry_emissor.bind("<FocusIn>", self.clear_placeholder)

        self.send_button = ctk.CTkButton(self.master, text="Enviar Mensagem", command=lambda: self.enviar_mensagem_emissor(serial_port_e), fg_color='#6a93a9', text_color="white")
        self.send_button.pack(pady=5)

        self.receber_mensagens(serial_port_e)

    def recetor_menu(self):
        self.label.configure(text="Menu do Recetor")
        self.emissor_button.pack_forget()
        self.recetor_button.pack_forget()
        self.create_text_box()

        global serial_port_r
        serial_port_r = serial.Serial(SERIAL_PORT_RECEIVER, 9600, timeout=2)

        self.receber_dados(serial_port_r)

        self.text_entry_recetor = ctk.CTkEntry(self.master, width=400)  # Caixa de entrada de texto para o recetor
        self.text_entry_recetor.pack(pady=5)
        self.text_entry_recetor.insert(0, "Escreva a sua mensagem...")
        self.text_entry_recetor.bind("<FocusIn>", self.clear_placeholder)

        self.send_mensagem_button = ctk.CTkButton(self.master, text="Enviar Mensagem", command=lambda: self.enviar_mensagem_recetor(serial_port_r), fg_color='#6c9562', text_color="white")
        self.send_mensagem_button.pack(pady=5)

    def create_text_box(self):
        self.text_box_frame = ctk.CTkFrame(self.master)
        self.text_box_frame.pack(pady=10)

        self.text_box = ctk.CTkTextbox(self.text_box_frame, width=500, height=350, wrap="word", state="disabled")
        self.text_box.pack(side="left", fill="both", expand=True)

        self.scrollbar = ctk.CTkScrollbar(self.text_box_frame, command=self.text_box.yview)
        self.scrollbar.pack(side="right", fill="y")

        self.text_box.configure(yscrollcommand=self.scrollbar.set)

    def adicionar_mensagem_text_box(self, mensagem, autor):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.text_box.configure(state="normal")
        if autor == "Emissor":
            self.text_box.insert("end", f"{mensagem}\n", ("emissor",))
            self.text_box.insert("end", f"{timestamp}\n", ("timestamp",))
        else:
            self.text_box.insert("end", f"{mensagem}\n", ("recetor",))
            self.text_box.insert("end", f"{timestamp}\n", ("timestamp",))
        self.text_box.see("end")  # Rolar para a última mensagem
        self.text_box.configure(state="disabled")

    def enviar_arquivo(self, serial_port):
        filename = filedialog.askopenfilename()
        filename = os.path.basename(filename)
        if filename:
            data_type = 1  # Você pode ajustar isso conforme necessário
            total_sequences = sum(1 for _ in split(filename))  # Calcula o total_sequences
            sequence_number = 0  # Inicializa sequence_number
            frame_layers = frame_layer(data_type, filename, sequence_number, total_sequences)  # Constrói as frame_layers
            send_thread = Thread(target=send_data, args=(serial_port, frame_layers,))
            send_thread.start()
            messagebox.showinfo("Sucesso", "Arquivo enviado com sucesso!")

    def receber_dados(self, serial_port):
        receive_thread = Thread(target=receive_data_receiver, args=(serial_port,))
        receive_thread.start()

        # Verifica periodicamente se há arquivos na fila
        self.master.after(1000, self.process_received_files)

    def receber_mensagens(self, serial_port):
        receive_thread = Thread(target=receive_data, args=(serial_port,))
        receive_thread.start()

        # Verifica periodicamente se há arquivos na fila
        self.master.after(1000, self.process_received_messages)

    def process_received_files(self):
        while not self.received_files_queue.empty():
            layer_7_frame = self.received_files_queue.get()
            frame_data = layer_7_frame
            mensagem = reconstruct_file(frame_data)  # Apenas um argumento
            if mensagem:
                self.adicionar_mensagem_text_box("Emissor: " + mensagem, "Emissor")
        # Verifica novamente após 1 segundo
        self.master.after(1000, self.process_received_files)

    def process_received_messages(self):
        while not received_frames_queue_sender.empty():
            layer_7_frame = received_frames_queue_sender.get()
            message = layer_7_frame[3:].decode('utf-8')
            self.adicionar_mensagem_text_box("Recetor: " + message, "Recetor")

        # Verifica novamente após 1 segundo
        self.master.after(1000, self.process_received_messages)

    def enviar_mensagem_emissor(self, serial_port):
        mensagem = self.text_entry_emissor.get()  # Obtém o texto da caixa de entrada do emissor
        if mensagem and mensagem != "Escreva a sua mensagem...":
            data_type = 2  # Define o tipo de dado como mensagem
            frame_layers = frame_layer(data_type, '', 0, mensagem)  # Constrói as frame_layers
            send_thread = Thread(target=send_data, args=(serial_port, frame_layers,))
            send_thread.start()
            self.adicionar_mensagem_text_box("Emissor: " + mensagem, "Emissor")
            self.text_entry_emissor.delete(0, "end")  # Limpa a caixa de entrada do emissor após o envio

    def enviar_mensagem_recetor(self, serial_port):
        mensagem = self.text_entry_recetor.get()  # Obtém o texto da caixa de entrada do recetor
        if mensagem and mensagem != "Escreva a sua mensagem...":
            data_type = 2  # Define o tipo de dado como mensagem
            frame_layers = frame_layer(data_type, '', 0, mensagem)  # Constrói as frame_layers
            send_thread = Thread(target=send_data_receiver, args=(serial_port, frame_layers,))
            send_thread.start()
            self.adicionar_mensagem_text_box("Recetor: " + mensagem, "Recetor")
            self.text_entry_recetor.delete(0, "end")  # Limpa a caixa de entrada do recetor após o envio

    def clear_placeholder(self, event):
        if event.widget.get() == "Escreva a sua mensagem...":
            event.widget.delete(0, "end")

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")  # Opcional: Define o modo de aparência (dark/light)
    ctk.set_default_color_theme("blue")  # Opcional: Define o tema de cores (blue/dark-blue/green)
    root = ctk.CTk()
    app = InterfaceGrafica(root)
    root.mainloop()