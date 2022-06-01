import multiprocessing as mp
import argparse
import sys
import time

def Eliminate_return_line(document):                                                          #fonction that eliminate all "\n" in the document
    for i in range(document.count(b"\n#")):
        first_commentary = document.find(b"\n#")                                              #position of the first "\n"
        last_commentary = document.find(b"\n#", first_commentary + 1)                         #position of the last "\n"
        document = document.replace(document[first_commentary:last_commentary], b"")
    return(document)

def Plain_PPM_format(document):                                                               #function that extract all the pixels from the document
    header = document[:15].decode()                                                           #decode the first 15 character of the document
    header = header.replace("P6", "P3")                                                       #get the magic number P3
    pixels_list = [x for x in document[15:]]                                                  #put all the pixels in a list
    return(header, pixels_list)

def Color_filter(color, c_queue, argument):                                                   #function which make all the filters for each color
    leido = b""
    pixels = ""
    count = 0
    while True:
        leido += c_queue.get()                                                                #we get the good queue and verify if she is not empty
        if c_queue.empty():
            break
    data = Eliminate_return_line(leido)
    header, pixels_list = Plain_PPM_format(data)
    if argument == 1:
        for i in range(0, (len(pixels_list)-3), 3):                                           #for each color, we calculate the value of the right triplet and setu up the two others at 0
            if color == 0:
                pixels_list[i] = round(pixels_list[i] * argument)
                pixels_list[i+1] = 0
                pixels_list[i+2] = 0
            elif color == 1:
                pixels_list[i] = 0
                pixels_list[i+1] = round(pixels_list[i+1] * argument)
                pixels_list[i+2] = 0
            elif color == 2:
                pixels_list[i] = 0
                pixels_list[i+1] = 0
                pixels_list[i+2] = round(pixels_list[i+2] * argument)
            else :
                print("Incorrect value !")
                sys.exit()
        for x in pixels_list:
            count += 1
            pixels += str(x) + " "
            if count % 12 == 0:                                                               #we want 12 values per line, so we will have 4 pixels per line in the document
                pixels += "\n"
        if color == 0:
            filter = open("red.ppm", "w")
        elif color == 1:
            filter = open("green.ppm", "w")
        elif color == 2:
            filter = open("blue.ppm", "w")
        else:
            print("Incorrect value !")
            sys.exit()
        filter.write(header + "\n")                                                          #we write all the data in the right filter
        filter.write(pixels)
        filter.close()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Open and read a .ppm document")            #we set up the parse
    parser.add_argument("-r", "--red", default=1, help="Escala para rojo")
    parser.add_argument("-g", "--green", default=1, help=" Escala para verde")
    parser.add_argument("-b", "--blue", default=1, help="Escala para azul")
    parser.add_argument("-s", "--size", default=1024, help="Bloque de lectura")
    parser.add_argument("-f", "--file", default="dog.ppm", help="Archivo a procesar")
    args = parser.parse_args()

    if args.red < 0 or args.blue < 0 or args.green < 0:                                      #we write functions to avoid errors
        print("The color cant have a negative value")
        sys.exit()
    if args.size < 0:
        print("The size of the data can't be negative")
        sys.exit()
    try:
        doc = open(args.file, " ")

    except FileNotFoundError:
        print("The document is not in the folder")
        sys.exit()

    red_queue = mp.Queue()                                                                    #we initialize the queues and put text into them
    green_queue = mp.Queue()
    blue_queue = mp.Queue()

    while True:
        text = doc.read(args.size + 15)
        red_queue.put(text)
        green_queue.put(text)
        blue_queue.put(text)
        if not text:
            break
    doc.close()
    red_son = mp.Process(target=Color_filter, args=(0, red_queue, args.red))                  #set up the sons(one for each color) and that target the filter's making function
    green_son = mp.Process(target=Color_filter, args=(1, green_queue, args.green))
    blue_son = mp.Process(target=Color_filter, args=(2, blue_queue,  args.blue))

    time.sleep(1)                                                                             #start and join the sons
    red_son.start()
    time.sleep(1)
    green_son.start()
    time.sleep(1)
    blue_son.start()

    red_son.join()
    green_son.join()
    blue_son.join()









