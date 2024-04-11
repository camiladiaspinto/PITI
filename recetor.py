import struct
import serial

def receive_single_byte(serial_port, expected_byte):
    attempts = 0
    while attempts < 10:
        received_byte = serial_port.read(1)
        if received_byte == expected_byte:
            print("Byte recebido:", received_byte.hex())
            return  # Sai do loop se o byte recebido for o esperado
        else:
            print("Byte recebido:", received_byte.hex())
            attempts += 1
            print(f"Tentativa {attempts} de 10. Tentando novamente...")

    print(f"Byte esperado {expected_byte.hex()} não recebido após 10 tentativas.")


def receive_frame(serial_port):
    # Encontrar o bit de início
    print(serial_port)
    start_bit = serial_port.read(1)
    #print("start bit fora do loop: ", start_bit)
    while start_bit != bytes([0x0E]):
        print("Erro: Bit de início inválido. Procurando novo início...")
        start_bit = serial_port.read(1)
        #print("start bit: ", start_bit)

    # Ler os campos de origem e destino
    end_org = serial_port.read(1)
    end_dest = serial_port.read(1)

    # Ler o número de sequência
    sequence_number = serial_port.read(1)

    # Ler o tamanho do payload
    tamanho = serial_port.read(1)
    print(tamanho)
    tamanho_int = int.from_bytes(tamanho, byteorder='big')
    print(tamanho_int)

    # Ler os dados e o erro de correção
    data = serial_port.read(tamanho_int)

    if tamanho_int <= 50:
        correction_error = serial_port.read(8)        
    elif tamanho_int <= 200:
        correction_error = serial_port.read(16)
    else:
        correction_error = serial_port.read(32)
    

    return start_bit, end_org, end_dest, sequence_number, tamanho, data, correction_error


if __name__ == "__main__":
    try:
        serial_port = serial.Serial('/dev/ttyUSB1', 9600, timeout=2)

        print("Conexão estabelecida com sucesso.")
    except serial.SerialException as e:
        print("Erro ao tentar abrir a porta:", e)
        exit() 

    try:
        #expected_byte = b'\x55'  # Byte esperado
        #receive_single_byte(serial_port, expected_byte)
        while True:
            start_bit, end_org, end_dest, sequence_number, tamanho, data, correction_error = receive_frame(serial_port)
            print("tipo de frame: ", receive_frame)
            if start_bit is not None and end_org is not None and end_dest is not None and sequence_number is not None and tamanho is not None and data is not None and correction_error is not None:
                print("Bit de Início:", start_bit)
                print("Campo de Origem:", end_org)
                print("Campo de Destino:", end_dest)
                print("Número de Sequência:", sequence_number)
                print("Tamanho do Payload:", tamanho)
                print("Dados Recebidos:", data)
                print("Erro de Correção:", correction_error)

                #print("Dados Recebidos:", data)
                #print("Erro de Correção:", correction_error)"""
   
    except KeyboardInterrupt:
        serial_port.close()
    except Exception as e:
        print("Erro durante a comunicação:", e)
    finally:
        serial_port.close()
