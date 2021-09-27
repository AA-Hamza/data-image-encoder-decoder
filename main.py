import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import sys

_ENCODING = 0
_DECODING = 1

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def default_usage():
    eprint(f"FOR ENCODING: {sys.argv[0]} encode <image name> [file name] [output name]")
    eprint(f"FOR DECODING: {sys.argv[0]} decode <image name> [output file]  ")
    exit()

def read_file(file_name):
    try:
        if (file_name != sys.stdin):
            with open(file_name, 'r') as data:
                message = data.read()
        else:
            message = sys.stdin.read()
    except OSError as err:
        eprint("OS error: {0}".format(err))
        exit()
    except:
        eprint("Unexpected error reading file:", sys.exc_info()[0])
        exit()

    return message

def write_file(file_name, message):
    try:
        if (file_name != sys.stdout):
            with open(file_name, 'w') as f:
                f.write(message)
        else:
            message = sys.stdout.write(message)
    except OSError as err:
        eprint("OS error: {0}".format(err))
        exit()
    except:
        eprint("Unexpected error reading file:", sys.exc_info()[0])
        exit()

    return message

def read_image(image_file_name):
    #print(image_file_name)
    try:
        im = np.array(Image.open(image_file_name))
    except OSError as err:
        eprint("OS error: {0}".format(err))
        exit()
    except:
        eprint("Unexpected error reading image:", sys.exc_info()[0])
        exit()
    return im 

def handle_arguments():
    image_file_name = None
    message_file_name = None
    output_image_file_name = None
    output_file_name = None
    mode = None
    if (len(sys.argv) == 1):
        default_usage()
    elif (len(sys.argv) > 2):
        if (sys.argv[1] == 'encode'):
            mode = _ENCODING
            image_file_name = sys.argv[2]
            if (len(sys.argv) == 4):
                image_file_name = sys.argv[2]
                message_file_name = sys.argv[3]
            elif (len(sys.argv) == 5):
                image_file_name = sys.argv[2]
                message_file_name = sys.argv[3]
                output_image_file_name = sys.argv[4]
            else:
                default_usage()

        elif (sys.argv[1] == 'decode'):
            mode = _DECODING
            image_file_name = sys.argv[2]
            if (len(sys.argv) == 4):
                output_file_name = sys.argv[3]
        else:
            default_usage()

    return mode, image_file_name, message_file_name, output_image_file_name, output_file_name

def to_3_bytes(n):
    # 0bfirstsecondthird
    first  = n>>16 & ((1<<8)-1)
    second = n>>8  & ((1<<8)-1)
    third  = n     & ((1<<8)-1)
    return (first, second, third)

def from_3_bytes(first, second, third):
    # 0bfirstsecondthird
    return (first<<16)|(second<<8)|third

def save_into_last_7_bits(arr, char):
    #arr(first, second, third)
    ascii_char = ord(char)
    if (ascii_char > 127):
        eprint("This character "+char+" Can't be encoded, Can't fit 7 bits, passing it")
        return arr
    first, second, third = arr
    first  = first>>3<<3
    second = second>>2<<2
    third  = third>>2<<2
    first  = (0b111 & ascii_char>>4) | first
    second = (0b11 & ascii_char>>2) | second
    third  = (0b11 & ascii_char) | third
    return (first, second, third)

def get_from_last_7_bits(first, second, third):
    #arr(first, second, third)
    first  = first &0b0000000111
    second = second&0b0000000011
    third  = third &0b0000000011
    return (first<<4)|(second<<2)|third


def main():
    mode, image_file_name, message_file_name, output_image_file_name, output_file_name = handle_arguments()

    image_array = read_image(image_file_name)
    if (len(image_array.shape) != 3):
        eprint("Unsupported format, the image isn't rgb 3 bytes")
        exit()
    _IMAGE_SHAPE = (image_array.shape[0], image_array.shape[1])
    _META_DATA_LEN_LOCATION = (0, 0)#_IMAGE_SHAPE[1]-2)
    _META_DATA_STEP_LOCATION = (0, 1)#_IMAGE_SHAPE[1]-1)

    if (mode == _ENCODING):
        if (message_file_name != None):
            message = read_file(message_file_name)
        else:
            print("Please enter message you want to encode, Ctrl+D to end")
            message = read_file(sys.stdin)

        if (output_image_file_name == None):
            output_image_file_name = 'encoded_'+image_file_name

        if (output_image_file_name.find('.') != -1):
            extension_location = len(output_image_file_name) - output_image_file_name[::-1].find('.')
            if (output_image_file_name[extension_location:] != 'png'):
                output_image_file_name = output_image_file_name[:extension_location]+'png'
        else:
            output_image_file_name += '.png'

        message = ''.join(message)      #Just to be in the safe side

        _MAX_POSSIBLE_MESSAGE = image_array.shape[0]*image_array.shape[1]-2

        if (len(message) > _MAX_POSSIBLE_MESSAGE):
            eprint("Message is too long for this image")
            exit()

        _STEP = _MAX_POSSIBLE_MESSAGE // len(message)
        if (_STEP > 2**(8*3)-1 or len(message) > 2**(8*3)-1):
            eprint("Max message length is "+str(2**(8*3)-1)+", Message will be cut to fit")
            _STEP = 2**(8*3)-1
            message = message[:(2**(8*3)-1)]
    
        image_array[_META_DATA_STEP_LOCATION[0]][_META_DATA_STEP_LOCATION[1]] = to_3_bytes(_STEP)
        image_array[_META_DATA_LEN_LOCATION[0]][_META_DATA_LEN_LOCATION[1]] = to_3_bytes(len(message))
        image_array = image_array.reshape((_IMAGE_SHAPE[0]*_IMAGE_SHAPE[1], 3))
        encoding_index = 2
        message_index = 0
        while (message_index < len(message)):
            #print(len(message), message_index, _MAX_POSSIBLE_MESSAGE, _STEP, encoding_index)
            char = message[message_index]
            image_array[encoding_index] = save_into_last_7_bits(image_array[encoding_index], char)
            encoding_index += _STEP
            message_index += 1

        image_array = image_array.reshape((*_IMAGE_SHAPE, 3))
        #print('steps ', *image_array[_META_DATA_STEP_LOCATION[0]][_META_DATA_STEP_LOCATION[1]])
        #print('len ', *image_array[_META_DATA_LEN_LOCATION[0]][_META_DATA_LEN_LOCATION[1]])
        Image.fromarray(image_array).save(output_image_file_name, quality=100, subsampling=0)
        exit(0)

    elif (mode == _DECODING):
        #print(image_array)
        message = ''
        #print('steps ', *image_array[_META_DATA_STEP_LOCATION[0]][_META_DATA_STEP_LOCATION[1]])
        #print('len ', *image_array[_META_DATA_LEN_LOCATION[0]][_META_DATA_LEN_LOCATION[1]])
        _STEP = from_3_bytes(*image_array[_META_DATA_STEP_LOCATION[0]][_META_DATA_STEP_LOCATION[1]])
        _MESSAGE_LEN = from_3_bytes(*image_array[_META_DATA_LEN_LOCATION[0]][_META_DATA_LEN_LOCATION[1]])
        image_array = image_array.reshape((_IMAGE_SHAPE[0]*_IMAGE_SHAPE[1], 3))
        
        #print(_STEP, _MESSAGE_LEN)

        decoding_index = 2
        message_index = 0
        while (message_index < _MESSAGE_LEN):
            message += chr(get_from_last_7_bits(*image_array[decoding_index]))
            decoding_index += _STEP
            message_index += 1

        if (output_file_name != None):
            write_file(output_file_name, message)
        else:
            write_file(sys.stdout, message)


        

if __name__ == "__main__":
    main()
