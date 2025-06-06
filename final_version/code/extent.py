import threading 
import queue
import time 
import numpy as np
import time 
import cv2
import pygame
import os
import math
from collections import Counter

"""
全局模块

功能：定义全局变量，启动线程，停止线程，停止所有线程

使用方法： from extent import * /from extent import start_thread, stop_thread, stop_all_threads.....

"""


display_text = ["", "", "",""] 
id_data=[""]
place=[""]
obj=[""]
t1,t2,t3,t4 = "", "", "", ""
running_thread_event = threading.Event()
threads = {}  # 全局线程字典
data_queue = queue.Queue(maxsize=1000)  # 设置队列最大容量
id_event = threading.Event()
detection_event = threading.Event()
text_event = threading.Event()
cast_event = threading.Event()


def start_thread(name, target, args=()):
    """启动线程并添加到全局线程字典"""
    if name in threads and threads[name].is_alive():
        print(f"线程 {name} 已经在运行中。")
    else:
        thread = threading.Thread(target=target, name=name, args=args, daemon=True)
        thread.start()
        threads[name] = thread
        print(f"线程 {name} 已启动。")

def stop_thread(name):
    """停止并从全局线程字典中移除线程"""
    if name in threads:
        thread = threads[name]
        if thread.is_alive():
            print(f"正在停止线程 {name}...")
            running_thread_event.clear()
            thread.join(timeout=1.0)
            if thread.is_alive():
                print(f"警告：线程 {name} 未能在超时内结束。")
        del threads[name]
        print(f"线程 {name} 已停止。")
    else:
        print(f"线程 {name} 不存在。")

def stop_all_threads():
    """停止所有线程"""
    for name in list(threads.keys()):
        stop_thread(name)
