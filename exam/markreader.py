import cv2
#import tensorflow as tf
from PIL import Image
#from matplotlib import pylab as plt
import numpy as np
import os
from django.conf import settings
import math
import pyocr , pyocr.builders
#from .logger import log_write

PATH= os.path.join( settings.BASE_DIR , "exam")
STATIC_PATH = os.path.join( settings.STATIC_ROOT , "exam" , "image" , "omr")

print( 'BASE_DIR %s'%PATH )
print( 'STATIC_PATH %s'%STATIC_PATH )

#Tesseract OCR
t_path = os.path.join( settings.BASE_DIR , "Tesseract-OCR")
if t_path not in os.environ["PATH"].split(os.pathsep):
    os.environ["PATH"] += os.pathsep + t_path
tools = pyocr.get_available_tools()
tool = tools[0]
# print("Will use tool '%s'" % (tool.get_name()))
langs = tool.get_available_languages()
# print("Available languages: %s" % ", ".join(langs))
lang = langs[2]

def ocr(image,split_cr=False,split_space=False):
    pilImg = Image.fromarray(np.uint8(image))
    txt = tool.image_to_string(
        pilImg, lang='eng', builder=pyocr.builders.TextBuilder(tesseract_layout=6)
    )

    if split_cr == True:
        txt = "".join( txt.split("\n"))

    if split_space == True:
        txt = "".join( txt.split(" "))
        txt = "".join( txt.split("　"))
    return txt

#画像を表示する
def imgshow(img):
    cv2.namedWindow("window", cv2.WINDOW_NORMAL)
    cv2.imshow('window', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

#２値画像に変換する
def bwchange(img):
    img_temp = cv2.GaussianBlur(img, (1, 1), 3)
    #imgshow( img_temp )
    res, img = cv2.threshold(img_temp, 50, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return res,img

# ５桁の数字を作る関数
def makenum(num):
    if num < 10:
        n = '0000' + str(num)
    elif num < 100:
        n = '000' + str(num)
    elif num < 1000:
        n = '00' + str(num)
    elif num < 10000:
        n = '0' + str(num)
    return n

def get_answer_list(filename):
    #マーカーの読み込み
    path = os.path.join( STATIC_PATH , "marker.png" )

    marker = cv2.imread(path, 0)
    
    #画像ファイルの読み込みとサイズ調整
    img = cv2.imread(filename, 0)
    #imgshow( img )
    img = cv2.resize(img, (2100, 2970))
    #imgshow( img )
    #print( ocr(img))
    #角度を調節する
    #res_gaku = cv2.matchTemplate(img, marker, cv2.TM_CCOEFF_NORMED)
    #threshold = 0.5
    #loc = np.where(res_gaku >= threshold)
    #print( loc )
    #min_x = min(loc[1])
    #min_y = min(loc[0])
    #max_x = max(loc[1])
    #max_y = max(loc[0])
    #print( "minx:%d,maxy:%d,miny:%d,maxy:%d"%(min_x,max_x,min_y,max_y))
    #x1 = max_x - min_x
    #y1 = max_y - min_y
    #rad1 = math.sqrt( x1*x1 + y1*y1)
    #print(math.degrees(math.asin(y1/rad1)))
    #rad = 90-math.degrees(math.asin(y1/rad1))
    #print( rad )
    #trans = cv2.getRotationMatrix2D((1050,1485), rad, 1.0)
    #img = cv2.warpAffine(img,trans,(2100,2970))
    #imgshow( img )
    #img = cv2.resize(img, (1000, 1500))
    # markeと同じ画像の位置を取得する
    res_gaku = cv2.matchTemplate(img, marker, cv2.TM_CCOEFF_NORMED)
    #print( res_gaku )
    threshold = 0.4
    loc = np.where(res_gaku >= threshold)
    #print( loc )
    x = min(loc[1])
    y = min(loc[0])
    mark_area = { 'x' : x , 'y' : y }
    mark_list =[]
    mark_list.append( mark_area )
    for pt in zip(*loc[::-1]):
        nx = pt[0]
        ny = pt[1]
        if y + 80 < ny:
            mark_area = {}
            mark_area['x'] = nx
            mark_area['y'] = ny
            mark_list.append( mark_area )
            y = ny

    #組織ID、テストID、ユーザIDを取得する
    img_info = img[mark_list[0]['y']-25: mark_list[0]['y']+140, mark_list[0]['x']+90: mark_list[0]['x']+1805]
    img_info = cv2.resize(img_info, (1400, 200))

    #imgshow( img_info )

    org_id = img_info[0:100, 348:695]
    test_id = img_info[0:100, 1050:1400]
    user_id = img_info[104:200, 348:695]
    #org_id = cv2.resize(org_id,(350,100))
    #test_id = cv2.resize(test_id,(350,100))
    #user_id = cv2.resize(user_id,(350,100))
    #imgshow( org_id )
    #imgshow( test_id )
    #imgshow( user_id )

    o_n = ocr(org_id)
    t_n = ocr(test_id)
    u_n = ocr(user_id)
    print("{} {} {}".format(o_n,t_n,u_n))
    # 列数
    n_col = 20
    #結果を入れる配列
    result = [[],[],[],[]]
    # マークシート
    # 全ての行が終わるまで
    for r in range(len( mark_list) ):
        if r >= 3:
            img_ans = img[ mark_list[r]['y']-15:mark_list[r]['y']+55 , mark_list[r]['x']+85: 1950]
            # リサイズ
            img_ans = cv2.resize(img_ans, (n_col * 30, 30))
            #img_ans = cv2.cvtColor( img_ans,cv2.COLOR_GRAY2RGBA)

            # 黒白に変換
            res_gaku, img_ans = bwchange(img_ans)
            #imgshow( img_ans )
            img_ans = 255 - img_ans
            #imgshow( img_ans )
            #1～20の答え
            area_sum1 = []
            for col in range(1,5):
                tmp_img = img_ans[5:90 , col * 30 : col * 30 + 30 ]
                #print( col )
                #imgshow( tmp_img )
                val = np.sum(tmp_img)
                #print( "%s,%s"%(col,val) )
                if val > 20000:
                    area_sum1.append(val)
                else:
                    area_sum1.append(0)
            result[0].append( area_sum1 > np.median(area_sum1) * 3)

            #21～40の答え
            area_sum2 = []
            for col in range(6,10):
                tmp_img = img_ans[5:90, col * 30: col * 30 + 30 ]
                #print( col )
                #imgshow( tmp_img )
                val = np.sum(tmp_img)
                if val > 20000:
                    area_sum2.append(val)
                else:
                    area_sum2.append(0)

            result[1].append( area_sum2 > np.median(area_sum2) * 3 )

            #41～60の答え
            area_sum3 = []
            for col in range(11,15):
                tmp_img = img_ans[5:90, col * 30: col * 30 + 30 ]
                #print( col )
                #imgshow( tmp_img )
                val = np.sum(tmp_img)
                if val > 20000:
                    area_sum3.append(val)
                else:
                    area_sum3.append(0)
            result[2].append( area_sum3 > np.median(area_sum3) * 3 )

            #61～80の答え
            area_sum4 = []
            for col in range(16,20):
                tmp_img = img_ans[5:90, col * 30: col * 30 +30 ]
                #print( col )
                #imgshow( tmp_img )
                val = np.sum(tmp_img)
                if val > 20000:
                    area_sum4.append(val)
                else:
                    area_sum4.append(0)
            result[3].append( area_sum4 > np.median(area_sum4) * 3 )

    answer = ['1', '2', '3', '4']
    answerlist = []
    # y=1→1～30 y=2→31～60 y=3→61～90
    for y in range(4):
        for x in range(len(result[y])):
            res = np.where(result[y][x] == True)[0]
            q = []
            if len(res) > 1:
                q.append(y * 20 + x + 1)
                q.append('複数回答')
            elif len(res) == 1:
                q.append(y * 20 + x + 1)
                q.append(answer[res[0]])

            else:
                q.append(y * 20 + x + 1)
                q.append('未回答')
            answerlist.append(q)

    return o_n,t_n,u_n, answerlist
