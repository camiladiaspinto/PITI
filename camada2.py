import time
import serial
from queue import Queue
import zlib

received_frames_queue = Queue() # lista de mensagens recebidas 
received_frames_queue_sender = Queue()  # lista de mensagens recebidas do emissor

# função para enviar dados do emissor (COM3)
def send_data(serial_port, layer_7_frame):
    try:
        start_bit = b'\x0E'
        end_org = b'\x01'
        end_dest = b'\x08'
        for frame_data in layer_7_frame:
            ack_received = False
            checksum = zlib.crc32(frame_data).to_bytes(4, 'big')
            frame_data_with_checksum = frame_data + checksum
            tamanho = len(frame_data_with_checksum)
            tamanho_bytes = int.to_bytes(tamanho, 1, 'big')
            frame = start_bit + end_org + end_dest + tamanho_bytes + frame_data_with_checksum
            print("Enviando a mensagem:", frame)
            serial_port.write(frame)

            while not ack_received:
                print("Esperando ACK ou NACK...")
                timeout = time.time() + 6
                while time.time() < timeout:
                    ack = serial_port.read(1)
                    if ack == b'\x06':
                        print("ACK recebido.")
                        ack_received = True
                        break
                    elif ack == b'\x07':
                        print("NACK recebido. Reenviando a trama...")
                        serial_port.write(frame)
                        break
                else:
                    print("Timeout: Reenviando a trama...")
                    serial_port.write(frame)
    except KeyboardInterrupt:
        serial_port.close()
    except serial.SerialException as e:
        print(f"Erro durante a comunicação: {e}")
    

# função para receber os dados do emissor (COM3)
def receive_data(serial_port, is_image=False, received_data_filename=None, reconstructed_image_filename=None):
    global tempototal
    try:
        tramasrecebidas = 0
        tempototal = 0.0
        while True:
            if serial_port.in_waiting > 0:
                start_byte = serial_port.read(1)
                if start_byte == b'\x0E':
                    starttime = time.time()
                    end_org = serial_port.read(1)
                    end_dest = serial_port.read(1)
                    tamanho = serial_port.read(1)
                    tamanho_int = int.from_bytes(tamanho, byteorder='big')

                    layer_7_frame = serial_port.read(tamanho_int)
                    checksum_received = layer_7_frame[-4:]
                    frame_data = layer_7_frame[:-4]
                    checksum_calculated = zlib.crc32(frame_data).to_bytes(4, 'big')

                    if checksum_received != checksum_calculated:
                        print("Erro: Checksum não corresponde. Dados corrompidos.")
                        NACK = b'\x07'
                        serial_port.write(NACK)
                        continue

                    print("Bit Start: ", start_byte)
                    print("Endereço de Origem:", end_org)
                    print("Endereço de Destino:", end_dest)
                    print("Tamanho do Payload:", tamanho)
                    print("Dados Recebidos:", layer_7_frame)

                    ACK = b'\x06'
                    serial_port.write(ACK)
                    received_frames_queue_sender.put(frame_data)
                    intervalo = time.time() - starttime
                    print("Tempo de envio da trama: {:.2f} segundos".format(intervalo))
                    print("Confirmo a receção com envio do ACK")

                    tempototal += intervalo
                    tramasrecebidas += 1
    except KeyboardInterrupt:
        serial_port.close()
    except Exception as e:
        print("Erro durante a comunicação:", e)
    finally:
        serial_port.close()


# função para enviar dados do receptor (COM4)
def send_data_receiver(serial_port, layer_7_frame):
    try:
        start_bit = b'\x0E'
        end_org = b'\x01'
        end_dest = b'\x08'
        for frame_data in layer_7_frame:
            ack_received = False
            checksum = zlib.crc32(frame_data).to_bytes(4, 'big')
            frame_data_with_checksum = frame_data + checksum
            tamanho = len(frame_data_with_checksum)
            tamanho_bytes = int.to_bytes(tamanho, 1, 'big')
            frame = start_bit + end_org + end_dest + tamanho_bytes + frame_data_with_checksum
            print("Enviando a mensagem:", frame)
            serial_port.write(frame)

            while not ack_received:
                print("Esperando ACK ou NACK...")
                timeout = time.time() + 6
                while time.time() < timeout:
                    ack = serial_port.read(1)
                    if ack == b'\x06':
                        print("ACK recebido.")
                        ack_received = True
                        break
                    elif ack == b'\x07':
                        print("NACK recebido. Reenviando a trama...")
                        serial_port.write(frame)
                        break
                else:
                    print("Timeout: Reenviando a trama...")
                    serial_port.write(frame)
    except KeyboardInterrupt:
        serial_port.close()
    except serial.SerialException as e:
        print(f"Erro durante a comunicação: {e}")

def receive_data_receiver(serial_port):
    global tempototal
    try:
        tramasrecebidas = 0
        tempototal = 0.0
        while True:
            if serial_port.in_waiting > 0:
                start_byte = serial_port.read(1)
                if start_byte == b'\x0E':
                    starttime = time.time()
                    end_org = serial_port.read(1)
                    end_dest = serial_port.read(1)
                    tamanho = serial_port.read(1)
                    tamanho_int = int.from_bytes(tamanho, byteorder='big')

                    layer_7_frame = serial_port.read(tamanho_int)
                    checksum_received = layer_7_frame[-4:]
                    frame_data = layer_7_frame[:-4]
                    checksum_calculated = zlib.crc32(frame_data).to_bytes(4, 'big')

                    if checksum_received != checksum_calculated:
                        print("Erro: Checksum não corresponde. Dados corrompidos.")
                        NACK = b'\x07'
                        serial_port.write(NACK)
                        continue

                    print("Bit Start: ", start_byte)
                    print("Endereço de Origem:", end_org)
                    print("Endereço de Destino:", end_dest)
                    print("Tamanho do Payload:", tamanho)
                    print("Dados Recebidos:", layer_7_frame)

                    ACK = b'\x06'
                    serial_port.write(ACK)
                    received_frames_queue.put(frame_data)
                    intervalo = time.time() - starttime
                    print("Tempo de envio da trama: {:.2f} segundos".format(intervalo))
                    print("Confirmo a receção com envio do ACK")

                    tempototal += intervalo
                    print("Tempo total de transmissão: {:.2f} segundos".format(tempototal))

                    tempototal += intervalo
                    tramasrecebidas += 1
    except KeyboardInterrupt:
        serial_port.close()
    except Exception as e:
        print("Erro durante a comunicação:", e)
    finally:
        serial_port.close()
