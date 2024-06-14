from threading import Thread
from datetime import datetime
import os
from PIL import Image
import io
from queue import Queue
from camada2 import send_data, receive_data,send_data_receiver, receive_data_receiver, received_frames_queue, received_frames_queue_sender


#função para reconstruir a imagem a partir do ficheiro de bytes
def reconstruct_image_from_file(received_data_filename, reconstructed_image_filename):
    try:
        with open(received_data_filename, 'rb') as file:
            image_bytes = file.read()
        
        image = Image.open(io.BytesIO(image_bytes))
        
        new_image_filename = reconstructed_image_filename.split('.')[0] + '_reconstructed.' + reconstructed_image_filename.split('.')[1]
        image.save(new_image_filename)
        print("Imagem reconstruída e gurdada como:", new_image_filename)
    except Exception as e:
        print("Erro ao reconstruir a imagem:", e)

sequence_number = 0
#funcao para dividir o ficheiro a enviar em blocos de 128 bytes
def split(input_file, block_size=128):
    with open(input_file, 'rb') as f:
        global sequence_number 
        while True:
            data = f.read(block_size)
            tamanho = len(data)
            if not data:
                break
            sequence_number += 1
            yield data

#funcao para reconstruir a trama do tipo 0
def reconstruct_file_data_type_0(layer_7_frame):
    sequence_number = layer_7_frame[1]
    total_sequences = int(sequence_number)
    filename = layer_7_frame[3:]
    filename_decode = filename.decode('utf-8')
    file_extension = filename_decode.split('.')[-1].lower()
    return filename_decode, total_sequences, file_extension

#global filename_decode, total_sequences, file_extension
#funcao a trama do tipo 1, com as variaveis da trama do tipo 0
def reconstruct_file(layer_7_frame):
    global filename_decode, total_sequences, file_extension
    data_type = layer_7_frame[0]
    img_save = 'imgsave'
    if data_type == 0:
        filename_decode, total_sequences, file_extension = reconstruct_file_data_type_0(layer_7_frame)
    elif data_type == 1:
        sequence_number = layer_7_frame[1]
        tamanho = layer_7_frame[2]
        data = layer_7_frame[3:]
        if sequence_number <= total_sequences:
            file_extension = filename_decode.split('.')[-1].lower()
            #quando a extensão é um ficheiro de texto
            if file_extension == 'txt':
                new_filename = filename_decode.split('.')[0] + '_reconstructed.' + filename_decode.split('.')[1]

                with open(new_filename, 'ab') as file:
                    print(data)
                    file.write(data)
                    print("Dados guardados no arquivo")
            #quando a extensão é um ficheiro de imagem
            elif file_extension in ['jpg', 'jpeg', 'png', 'gif']:
                with open(img_save, 'ab') as file:
                    file.write(data)
                    print("Dados guardados no arquivo")
                if sequence_number == total_sequences:
                    reconstruct_image_from_file(img_save, filename_decode)
                    print("Arquivo de imagem reconstruído:", filename_decode)
                    os.remove(img_save)  # Remove o arquivo temporário após a reconstrução da imagem
            else:
                print("Arquivo de extensão desconhecida:", data)
    elif data_type == 2:
        sequence_number = layer_7_frame[1]
        tamanho = layer_7_frame[2]
        message = layer_7_frame[3:].decode('utf-8')
        return message  
    else:
        print("Tipo de dados inválido.")
        return None

#funcao para criar a trama do tipo 0
def create_start_frame(data_type,filename,total_sequences):
    data_type_bytes = bytes([data_type])
    total_sequences_bytes=total_sequences.to_bytes(1,'big')
    filename_bytes = filename.encode('utf-8')
    filename_length_bytes = len(filename_bytes).to_bytes(1, 'big')
    start_frame = data_type_bytes  + total_sequences_bytes+ filename_length_bytes+filename_bytes 
    return start_frame

#funcao para construir as tramas do tipo 1 e 2
def frame_layer(data_type, filename,sequence_number,total_sequences): 
    frame_layers = [] 
    if data_type == 1:  # Se for um ficheiro de texto ou imagem 
        start_frame = create_start_frame(0, filename,total_sequences)
        frame_layers.append(start_frame)
        for data in split(filename):
            data_type_bytes = data_type.to_bytes(1, 'big')
            tamanho = len(data)
            tamanho_bytes = tamanho.to_bytes(1, 'big')
            sequence_number +=1 
            sequence_number_bytes = sequence_number.to_bytes(1, 'big')
            frame_layer_7 =  data_type_bytes + sequence_number_bytes+tamanho_bytes+data
            frame_layers.append(frame_layer_7) 
    elif data_type == 2:  # Se for uma mensagem
        data_type_bytes = data_type.to_bytes(1, 'big')
        tamanho = len(total_sequences.encode('utf-8')) 
        tamanho_bytes = tamanho.to_bytes(1, 'big')
        sequence_number += 1
        sequence_number_bytes = sequence_number.to_bytes(1, 'big')
        frame_layer_7 = data_type_bytes + sequence_number_bytes + tamanho_bytes + total_sequences.encode('utf-8')
        frame_layers.append(frame_layer_7)
    return frame_layers