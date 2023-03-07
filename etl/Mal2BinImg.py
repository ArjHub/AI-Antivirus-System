'@author:NavinKumarMNK'
# Path: etl/Mal2BinImg.py
import os
import argparse
import numpy as np
from PIL import Image
from math import log
import uuid

def bytes2img(data_path):
    # read the data from the given path
    name = os.path.basename(data_path)
    with open(data_path, "rb") as f:
        array = []
        for line in f:
            xx = line.split()
            if len(xx) != 17:
                continue
            array.append([int(i, 16) if i != b'??' else 0 for i in xx[1:]])

        # convert the array to image
        array = np.array(array)
        if array.shape[1] != 16:  # If not hexadecimal
            assert(False)

        b = int((array.shape[0]*16)**(0.5))
        b = 2**(int(log(b)/log(2))+1)
        a = int(array.shape[0]*16/b)
        array = array[:a*b//16, :]
        array = np.reshape(array, (a, b))
        im = Image.fromarray(np.uint8(array))

        del array
        return im

def dataset_gen(data_path, save_path):
    # generate the dataset
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    for root, dirs, files in os.walk(data_path):
        for file in files:
            if file.endswith(".bytes"):
                im = bytes2img(os.path.join(root, file))
                im.save(os.path.join(save_path, file[:-4]+".png"))


def file2hex(name, file_path, data_path):
    os.system("hexdump -v  -e '" + '"%08.8_ax  "' + "' -e' 4/1 " + '"%02x " " " 4/1 "%02x " " "  4/1 "%02x " " " 4/1 "%02x "  ' +
              "' -e '" + '"\n"' + "' " + file_path + " >" + data_path + "/data/bytes/" + name +".bytes")
    
def file2asm(name, file_path, data_path):
    os.system("objdump -d " + file_path + " > " + data_path +
              + name +".asm")

def file_conv(file_path, data_path):
    # convert the file to bytes and asm
    filename = os.path.basename(file_path)
    hex_filename = uuid.uuid4().hex
    
    file2hex(file_path, data_path)
    file2asm(file_path, data_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_path', type=str, default='./data/malware', help='path to the malware data')
    parser.add_argument('--save_path', type=str, default='./data/malware_img', help='path to save the malware image')
    args = parser.parse_args()
    dataset_gen(args.data_path, args.save_path)
