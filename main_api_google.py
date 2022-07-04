import os
import shutil
import string
import time
import tkinter.ttk
from tkinter import *
from tkinter import filedialog
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from unidecode import unidecode
import random
import re
from subprocess import CREATE_NO_WINDOW
from threading import Thread

import apiGoogle
from utility import *

link_cmt = "https://vocr.vn/"
link_gplx = '//*[@id="root"]/div[2]/div/div[2]/div/div[1]/a[2]'
upload = '//*[@id="gatsby-focus-wrapper"]/section/section/main/div/div/div[5]/div/div[1]/span/div/span/div'
upload2 = '//*[@id="gatsby-focus-wrapper"]/section/section/main/div/div/div[5]/div/div[1]/span/div/span/input'
upload3 = '//*[@id="root"]/div[2]/div/div[2]/div/div[2]/div[1]/div/div[3]/label/input'
xu_ly = '//*[@id="gatsby-focus-wrapper"]/section/section/main/div/div/div[5]/div/div[1]/button'
info = '//*[@id="gatsby-focus-wrapper"]/section/section/main/div/div/div[5]/div/div[2]/div/div'
info2 = '//*[@id="root"]/div[2]/div/div[2]/div/div[2]/div[2]/div/div[2]/div/div'

mydict_cmt = {"So the:": ID, "Ho ten:": FULL_NAME, "Ngay sinh:": BIRTHDAY, "Thuong tru:": ADDRESS}
mydict_gplx = {"So the:": ID, "Ho ten:": FULL_NAME, "Ngay sinh:": BIRTHDAY, "Noi cu tru:": ADDRESS}

info_dict = {'ho_ten': FULL_NAME, 'id': ID, 'ngay_sinh': BIRTHDAY, 'noi_thuong_tru': ADDRESS, 'que_quan': 'que_quan'}

res_info_final = ""
folder_image = ""
zip_code = dict()
pattern = "^.*(?=.{8,})(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@#$%^&+=]).*$"

extractInfor = []

image_extensions = ['jpg', 'jpeg', 'raw', 'bmp', 'heic']


# add check file co phai anh hay k?
def file_is_image(dir_path):
    extension = str(dir_path).split('.')[-1]
    extension = extension.lower()
    if extension in image_extensions:
        return True
    return False


def func_select_folder():
    global folder_image
    folder_image = filedialog.askdirectory()


def get_info(get_type):
    global res_info_final, folder_image
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    # options.add_experimental_option("excludeSwitches", ["ignore-certificate-errors"])
    # options.add_argument('headless')
    # options.add_argument('window-size=0x0')

    # clear output file
    # output file in selected folder + output
    dir_out = os.path.join(folder_image, 'output')
    if os.path.isdir(dir_out):
        shutil.rmtree(dir_out)

    cmt_folder = os.path.join(folder_image, 'CMT')
    if os.path.isdir(cmt_folder):
        if not os.path.isdir(cmt_folder):
            os.mkdir(cmt_folder)
        shutil.rmtree(cmt_folder)

    cccd_folder = os.path.join(folder_image, 'CCCD')
    if os.path.isdir(cccd_folder):
        if not os.path.isdir(cccd_folder):
            os.mkdir(cccd_folder)
        shutil.rmtree(cccd_folder)

    # chon folder anh muon lay thong tin
    list_image_dirs = []
    for root_dir, dirs, files in os.walk(folder_image):
        for file in files:
            dir_1 = os.path.join(root_dir, file)
            dir_2 = dir_1.replace('/', '\\')
            if file_is_image(dir_2):  # add neu la anh thi moi add vao
                list_image_dirs.append(dir_2)
    print(list_image_dirs)

    outlink = os.path.join(dir_out, "solamviec.xlsx")
    global outputFileName
    outputFileName = outlink.replace('/', '\\')
    print(outputFileName)

    if not os.path.isdir(dir_out):
        os.mkdir(dir_out)

    # Get zipcode in zipcode file
    file_zip = open('plugins/zipcode.txt', 'r')
    for line in file_zip:
        address = line.split(':')[0]
        address = address.lower()
        code = line.split(':')[1].replace('\n', '')
        if '-' in code:
            code = code.split('-')[0]
        zip_code[address] = code
    file_zip.close()

    parent_folder = folder_image.replace('/', '\\') + '\\'

    # get info
    cnt = 0
    extractInfor.clear()
    for list_image_dir in list_image_dirs:
        cnt += 1
        # file name
        file_name = list_image_dir.split('\\')[-1]
        file_name = file_name.split('.')[0]

        child_folder = list_image_dir.replace(parent_folder, '')

        if '\\' in child_folder:
            child_folder = child_folder.split('\\')[0]
        else:
            child_folder = parent_folder.split('\\')[-2]

        dict_txt = dict()

        # get thong tin
        mID, mName, mBirth, mAddr, typeID = None, None, None, None, None
        try:
            mID, mName, mBirth, mAddr, typeID = apiGoogle.get_full_info(list_image_dir)
        except:
            print("xu ly anh loi")

        # add neu khong lay duoc thong tin nao thi skip
        if mID is None or mAddr is None or mName is None or mBirth is None:
            continue

        dict_txt[ID] = mID
        dict_txt[FULL_NAME] = mName
        dict_txt[BIRTHDAY] = mBirth
        dict_txt[ADDRESS] = mAddr
        mAddrL = mAddr.lower()
        pass_pay = ''
        while not re.findall(pattern, pass_pay):
            pass_pay = ''.join(
                random.choice(string.ascii_uppercase + string.ascii_lowercase
                              + string.digits + "@#^&*") for _ in range(10))

        dict_txt[PASS_PAYPAL] = pass_pay
        dict_txt[FOLDER] = child_folder
        # parse zipcode
        dict_txt[ZIPCODE] = ""  # defaul zipcode
        if dict_txt.get(ADDRESS):
            for key in zip_code.keys():
                if key in mAddrL:
                    dict_txt[ZIPCODE] = zip_code[key]

        # copy CMT and CCCD
        cur_folder = parent_folder + child_folder
        print(cur_folder)
        os.chmod(cur_folder, 0o777)
        if 'CMT' in typeID:
            shutil.copytree(cur_folder, cmt_folder+'\\'+child_folder)
        else:
            shutil.copytree(cur_folder, cccd_folder+'\\'+child_folder)

        extractInfor.append(dict_txt)


class Main(object):
    def __init__(self, master):
        self.master = master
        button1 = Button(master, text='Select folder', command=func_select_folder)
        button1.grid(row=1, column=0, pady=10, padx=10)
        button2 = Button(master, text='Get CMT Info', command=lambda x="CMT": self.get_info_image(x))
        button2.grid(row=1, column=1, pady=10, padx=10)
        button2 = Button(master, text='Get GPLX Info', command=lambda x="GPLX": self.get_info_image(x))
        button2.grid(row=1, column=2, pady=10, padx=10)
        self.progress = tkinter.ttk.Progressbar(master, length=280, orient=HORIZONTAL, mode='indeterminate')
        # self.progress.grid(row=2, column=0, columnspan=3, padx=5, pady=10)

    def monitor_convert(self, thread):
        if thread.is_alive():
            self.master.after(100, lambda: self.monitor_convert(thread))
        else:
            self.progress.stop()
            self.progress.grid_forget()
            print(extractInfor)
            print_excel(extractInfor, outputFileName)
            print("done")

    def get_info_image(self, type_get):
        get_info_thread = GetInfo(type_get)
        get_info_thread.start()
        self.monitor_convert(get_info_thread)
        self.progress.grid(row=2, column=0, columnspan=3, padx=5, pady=10)
        self.progress.start()


class GetInfo(Thread):
    def __init__(self, type_get):
        super().__init__()
        self.type = type_get

    def run(self):
        get_info(self.type)


root = Tk()
app = Main(root)
root.title('Image to Text')
root.mainloop()
