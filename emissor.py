import struct
import time
import serial


def split(input_file, block_size=128):
    with open(input_file, 'rb') as f:
        sequence_number = 0
        while True:
            data = f.read(block_size)
            tamanho=len(data)
            #print(tamanho)
            if not data:
                break
            sequence_number += 1
           # print(f'Bloco {sequence_number}: {data}')
            yield data, sequence_number

def bits_correction_error(tamanho, data):
    #print(tamanho)
    if tamanho <= 50:
        tamanho_correction_error = 8
    
    elif tamanho <= 200:
        tamanho_correction_error = 16
    
    else:
        tamanho_correction_error = 32
    

    bloco = b'\x00' * tamanho_correction_error
    return bloco

def build_frame(data, sequence_number):
    start_bit = b'\x0E'
    end_org = b'\x01'
    end_dest = b'\x08'

   # print(sequence_number)

    sequence_number_bytes = int.to_bytes(sequence_number,1,'big')
    print(sequence_number_bytes)

    tamanho = len(data)
    print(tamanho)


    tamanho_bytes = int.to_bytes(tamanho,1,'big')
    print(tamanho_bytes)
    correction_error = bits_correction_error(tamanho,data)
    print(type(correction_error))


    frame= start_bit + end_org + end_dest + sequence_number_bytes + tamanho_bytes + data + correction_error

   # print(frame)
    return frame



"""def send_single_byte(serial_port):
    byte_to_send = b'\x55'  # Byte a ser enviado

    print("Enviando byte:", byte_to_send.hex())
    serial_port.write(byte_to_send)
   # serial_port.flush()"""



if __name__ == "__main__":
    input_file = input("Insira o nome do ficheiro: ")

    try:
        serial_port = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
        print("Conexão estabelecida com sucesso.")
    except serial.SerialException as e:
        print("Erro ao tentar abrir a porta:", e)
        exit() 

    
    try:
        #send_single_byte(serial_port)
        #print("Byte enviado com sucesso.")
        for data, sequence_number in split(input_file):
            frame = build_frame(data, sequence_number)
            print("Enviando a mensagem: ", frame)
            serial_port.write(frame)
            time.sleep(2)
          
   
    except KeyboardInterrupt:
        serial_port.close()
    except Exception as e:
        print("Erro durante a comunicação:", e)
    finally:
        serial_port.close()
