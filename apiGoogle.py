import re
from unidecode import unidecode
from datetime import datetime
# Imports the Google Cloud client library
from google.cloud import vision
import io
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "plugins/key/xenon-axe-354315-6da002141bae.json"


def detect_text_english(path):
    """Detects text in the file."""
    client = vision.ImageAnnotatorClient()

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.text_detection(image=image)

    texts = response.text_annotations
    text_result = ""

    for text in texts:
        text_vi = text.description
        text_en = unidecode(text_vi)
        if ' ' in text_en:
            text_result += text_en + '\n'

    text_list = text_result.split('\n')
    print(text_result)

    # if response.error.message:
    #     raise Exception(
    #         '{}\nFor more info on error messages, check: '
    #         'https://cloud.google.com/apis/design/errors'.format(
    #             response.error.message))

    return text_list


remove_list = ['CONG HOA', 'Doc lap', 'CAN CUOC', 'CHUNG MINH', 'Ho va ten', 'Gioi tinh', 'Quoc tich']


def get_full_info(path):
    text_res = detect_text_english(path)
    remove_list = ['CONG HOA', 'Doc lap', 'CAN CUOC', 'CHUNG MINH', 'Ho va ten', 'Gioi tinh', 'Quoc tich']

    def get_type():
        for v in text_res:
            if 'CAN CUOC' in v:
                return 'CCCD'
            elif 'CHUNG MINH' in v:
                return "CMT"
        return None

    def remove_by_text(s):
        for v in text_res:
            if s in v:
                text_res.remove(v)

    def remove_text():
        rm = set()
        for v in text_res:
            if re.fullmatch('[A-Z]+', v):
                rm.add(v)
        for v in text_res:
            for k in remove_list:
                if v.startswith(k):
                    rm.add(v)
        for v in rm:
            text_res.remove(v)

    def getID():
        for v in text_res:
            res = re.findall('[\d]+', v)
            for k in res:
                if int(k) > 10000:
                    return k

    def getBirth():
        rm = set()
        birth = datetime.today()
        for v in text_res:
            res = re.findall('\d{2}/\d{2}/\d{4}', v)
            if len(res) > 0:
                res_date = res[0]
                rm.add(res_date)
                tmp = datetime.strptime(res_date, '%d/%m/%Y')
                if tmp < birth:
                    birth = tmp
        for v in rm:
            for k in text_res:
                if v in k:
                    text_res.remove(k)
        remove_by_text('nam sinh')
        return birth.strftime('%d/%m/%Y')

    def getName():
        for v in text_res:
            vv = v.strip().replace(' ', '')
            if re.fullmatch('[A-Z]+', vv):
                return v

    def getAddr():
        arrs = []
        for v in text_res:
            tmp = re.findall('[\s\S]+,[\s\S]+,[\s\S]+', v)
            if len(tmp) > 0:
                arrs.append(tmp[0])
        if len(arrs) > 0:
            vv = arrs[-1]
            if vv.startswith(' '):
                vv = vv[1:]
            return vv

        if 'tru:' in ss:
            v = ss.split(':')[-1]
            if '\"' in v:
                v = v.replace('\"', '')
            if v.startswith(' '):
                v = v[1:]
            return v

    typeID = get_type()
    remove_text()

    ID = getID()
    remove_by_text(ID)
    birth = getBirth()
    remove_by_text(birth)
    full_name = getName()
    remove_by_text(full_name)

    for v in remove_list:
        remove_by_text(v)

    ss = ""
    for v in text_res:
        ss += v + ' '

    addr = getAddr()

    return ID, full_name, birth, addr, typeID
