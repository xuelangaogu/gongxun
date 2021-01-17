import sensor,image,lcd,utime
import KPU as kpu
from machine import UART
from fpioa_manager import fm
from Maix import GPIO
from board import board_info

lcd.init()
sensor.reset()
sensor.set_vflip(True)
sensor.set_hmirror(True)
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.set_windowing((224, 224))

sensor.run(1)
sensor.skip_frames(time = 2000)   #感光元件是有2s的时间来自动调节亮度和颜色的，初始化前的环境亮度会影响延时后的感光亮度

labels = 0
objects = 0
uart_A = UART(UART.UART1, 115200, 8, None, 1, timeout=1000, read_buf_len=4096)

class stuff(object):
    ID = 0
stuff = stuff()

def uartInit():
    fm.register(board_info.PIN15,fm.fpioa.UART1_TX)
    fm.register(board_info.PIN17,fm.fpioa.UART1_RX)

def Init_Task():
    global labels
    global objects
    objects = kpu.load("/sd/laji.kmodel")
    f=open("anchors.txt","r")
    anchor_txt=f.read()
    L=[]
    for i in anchor_txt.split(","):
        L.append(float(i))
    anchor=tuple(L)
    f.close()
    a = kpu.init_yolo2(objects, 0.6, 0.3, 5, anchor)
    f=open("classes.txt","r")
    labels_txt=f.read()
    labels = labels_txt.split(",")
    f.close()

def Object_Detection(img,obj):
    global labels
    code = kpu.run_yolo2(obj, img)
    if code != None:
        for i in code:
            a=img.draw_rectangle(i.rect(),(0,255,0),2)
        print(i.classid())
        stuff.ID = i.classid()
        #uart_A.write(pack_obj_data())
        print(pack_obj_data())

def pack_obj_data():
    pack_data=bytearray([0xAA,0x29,0x00,
        int(stuff.ID)>>8,int(stuff.ID),
        0x00])
    stuff.ID = 0
    lens = len(pack_data)#数据包大小

    i = 0
    sum = 0

    #和校验
    while i<(lens-1):
        sum = sum + pack_data[i]
        i = i+1
    pack_data[2] = sum;

    return pack_data

uartInit()
Init_Task()

while(True):
    img = sensor.snapshot()
    Object_Detection(img,objects)


#a = kpu.deinit(task)
