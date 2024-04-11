import struct
import time
import serial
import socket
from threading import Thread
from datetime import datetime

# Função para dividir o arquivo em blocos
def split(input_file, block_size=128):
    with open(input_file, 'rb') as f:
        sequence_number = 0
        while True:
            data = f.read(block_size)
            tamanho = len(data)
            if not data:
                break
            sequence_number += 1
            yield data, sequence_number

# Função para calcular o erro de correção
def bits_correction_error(tamanho, data):
    if tamanho <= 50:
        tamanho_correction_error = 8
    elif tamanho <= 200:
        tamanho_correction_error = 16
    else:
        tamanho_correction_error = 32
    bloco = b'\x00' * tamanho_correction_error
    return bloco

# Função para construir o quadro
def build_frame(data, sequence_number):
    start_bit = b'\x0E'
    end_org = b'\x01'
    end_dest = b'\x08'

    sequence_number_bytes = int.to_bytes(sequence_number, 1, 'big')
    tamanho = len(data)
    tamanho_bytes = int.to_bytes(tamanho, 1, 'big')
    correction_error = bits_correction_error(tamanho, data)

    frame = start_bit + end_org + end_dest + sequence_number_bytes + tamanho_bytes + data + correction_error
    return frame

# Função para enviar dados
ack_received = False
def send_data(serial_port, input_file):
    global ack_received
    try:
        for data, sequence_number in split(input_file):
            frame = build_frame(data, sequence_number)
            print("Enviando a mensagem:", frame)
            serial_port.write(frame)
            print(datetime.now())
            
            # Espera pela confirmação ACK
            timeout = time.time() + 3  # Tempo limite de 3 segundos, uma vez que a tempo de transmissão é de +/- 3 minutos 
            while  not ack_received:
                #print("entrei")
                if time.time() > timeout:
                    print("Timeout: Reenviando quadro...")

                    serial_port.write(frame)
                    timeout = time.time() + 5
                ack = serial_port.read(1)
                if ack == b'\x06':  # ACK recebido
                    print("ACK recebido.")

                    ack_received=True
                    break
            ack_received=False
    except KeyboardInterrupt:
        serial_port.close()
    except Exception as e:
        print("Erro durante a comunicação:", e)
    finally:
        serial_port.close()

# Função para receber dados
def receive_data(serial_port):
    try:
        while True:
            start_bit, end_org, end_dest, sequence_number, tamanho, data, correction_error = receive_frame(serial_port)
            print(datetime.now())
            if all((start_bit, end_org, end_dest, sequence_number, tamanho, data, correction_error)):
                print("Bit de Início:", start_bit)
                print("Campo de Origem:", end_org)
                print("Campo de Destino:", end_dest)
                print("Número de Sequência:", sequence_number)
                print("Tamanho do Payload:", tamanho)
                print("Dados Recebidos:", data)
                print("Erro de Correção:", correction_error)
                
                # Envia ACK para confirmar a recepção
                ACK= b'\x06'

                #time.sleep(5)
                serial_port.write(ACK)  # ACK
                #print(ACK)
                print("Confirmo a receção com envio do ACK")
    except KeyboardInterrupt:
        serial_port.close()
    except Exception as e:
        print("Erro durante a comunicação:", e)
    finally:
        serial_port.close()

# Função para receber quadro
def receive_frame(serial_port):
    start_bit = serial_port.read(1)
    while start_bit != bytes([0x0E]):
        print("Erro: Bit de início inválido. Procurando novo início...")
        start_bit = serial_port.read(1)

    end_org = serial_port.read(1)
    end_dest = serial_port.read(1)
    sequence_number = serial_port.read(1)
    tamanho = serial_port.read(1)
    tamanho_int = int.from_bytes(tamanho, byteorder='big')
    data = serial_port.read(tamanho_int)

    if tamanho_int <= 50:
        correction_error = serial_port.read(8)        
    elif tamanho_int <= 200:
        correction_error = serial_port.read(16)
    else:
        correction_error = serial_port.read(32)

    return start_bit, end_org, end_dest, sequence_number, tamanho, data, correction_error

if __name__ == "__main__":
    mode = input("Digite 'E' para emissor ou 'R' para receptor: ").upper()

    if mode == 'E':
        input_file = input("Insira o nome do arquivo: ")
        try:
            serial_port = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
            print("Conexão estabelecida com sucesso.")
        except serial.SerialException as e:
            print("Erro ao tentar abrir a porta:", e)
            exit() 

        send_thread = Thread(target=send_data, args=(serial_port, input_file))
        send_thread.start()
    elif mode == 'R':
        try:
            serial_port = serial.Serial('/dev/ttyUSB1', 9600, timeout=2)
            print("Conexão estabelecida com sucesso.")
        except serial.SerialException as e:
            print("Erro ao tentar abrir a porta:", e)
            exit() 

        receive_thread = Thread(target=receive_data, args=(serial_port,))
        receive_thread.start()
    else:
        print("Modo inválido. Digite 'E' para emissor ou 'R' para receptor.")
