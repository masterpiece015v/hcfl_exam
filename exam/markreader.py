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
STATIC_PATH = os.path.join( settings.STATIC_ROOT , "exam" , "data")

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
print( lang )
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

"""
class Ainum:
    sess = tf.compat.v1.InteractiveSession()
    #入力データ
    x = tf.compat.v1.placeholder("float",shape=[None,784])
    #正解データ
    y_ = tf.compat.v1.placeholder( "float" ,shape=[None,10])

    def weight_variable( shape ):
        initial = tf.random.truncated_normal( shape,stddev=0.1)
        return tf.Variable(initial)

    def bias_variable( shape ):
        initial = tf.constant( 0.1, shape=shape)
        return tf.Variable( initial )

    def conv2d( x,W ):
        return tf.nn.conv2d( x , W , strides=[1,1,1,1], padding='SAME')

    def max_pool_2x2( x ):
        return tf.nn.max_pool2d( x,ksize=[1,2,2,1],strides=[1,2,2,1],padding='SAME' )
        #return tf.nn.max_pool( x,ksize=[1,2,2,1],strides=[1,2,2,1],padding='SAME' )
        #return tf.nn.max_pool(x,ksize=[1,2,2,1],strides=[1,2,2,1],padding='SAME' )
        #return tf.nn.max_pool3d( x, ksize=[1,2,2,1],strides=[1,2,2,1],padding='SAME' )

    W_conv1 = weight_variable([5,5,1,32])
    b_conv1 = bias_variable([32])

    x_image = tf.reshape(x,[-1,28,28,1])

    h_conv1 = tf.nn.relu( conv2d(x_image,W_conv1) + b_conv1)
    h_pool1 = max_pool_2x2( h_conv1 )

    W_conv2 = weight_variable( [5,5,32,64] )
    b_conv2 = bias_variable([64])

    h_conv2 = tf.nn.relu( conv2d(h_pool1,W_conv2) + b_conv2)
    h_pool2 = max_pool_2x2( h_conv2 )

    W_fc1 = weight_variable([7*7*64,1024])
    b_fc1 = bias_variable( [1024] )

    h_pool2_flat = tf.reshape( h_pool2,[-1,7*7*64])

    h_fc1 = tf.nn.relu( tf.matmul(h_pool2_flat,W_fc1) + b_fc1 )

    keep_prob = tf.placeholder("float")
    h_fc1_drop = tf.nn.dropout( h_fc1,keep_prob)

    W_fc2 = weight_variable( [1024,10] )
    b_fc2 = bias_variable( [10] )

    #y_conv = tf.nn.softmax( tf.matmul( h_fc1_drop , W_fc2 ) + b_fc2 )
    y_conv = tf.nn.softmax( tf.matmul( h_fc1 , W_fc2 ) + b_fc2 )
    sess.run( tf.initialize_all_variables() )

    saver = tf.compat.v1.train.Saver()

    #django用設定
    #path = settings.BASE_DIR
    #print( path )
    #ローカル実行用設定
    #path = "C:\\PythonProject\\examsite"

    saver.restore( sess, os.path.join(PATH,"CNN","CNN.ckpt"))
    print("学習データを読み込みました")

    def get_num(self,source):
        img = Image.fromarray( source ).convert('L')
        plt.imshow( img )
        img.thumbnail((28,28))

        img = np.array(img,dtype=np.float32)
        img = 1 - np.array( img / 255 )
        img = img.reshape( 1 , 784 )

        p = self.sess.run( self.y_conv, feed_dict={self.x:img , self.y_:[[0.0] * 10], self.keep_prob:0.5})[0]

        return np.argmax(p)
"""
"""
#数字を中央に寄せる
def img_center( img ):
    #画像のサイズを取得
    r_max = len(img)
    c_max = len(img[0])
    r_top = r_max   #縦位置の始まり
    r_bottom = 0    #縦位置の終わり
    c_left = c_max  #横位置の始まり
    c_right = 0     #横位置の終わり

    #文字の縦位置、横位置を調べる
    for r in range( r_max ):
        for c in range( c_max ):
            if img[r][c] < 10:
                if r_top > r:
                    r_top = r

                if r_bottom < r:
                    r_bottom = r

                if c_left > c:
                    c_left = c

                if c_right < c:
                    c_right = c

    #横中央値
    c_mid = int( ( c_max/2 - ( c_right + c_left ) / 2) )
    #縦中央値
    r_mid = int( (r_max/2 - ( r_top + r_bottom) / 2))
    #print( 'r_max:%d,r_top:%d,r_bottom:%d,r_mid:%d,c_mid:%d'%(r_max,r_top,r_bottom,r_mid,c_mid) )

    #横位置を調整する
    if c_mid > 0:#右にずらす
        for r in range( r_max ):
            c = c_max - 1
            while c > c_mid:
                img[r][c] = img[r][c - c_mid]
                c = c - 1
        for r in range( r_max ):
            c = c_left + c_mid - 1
            while c > 0:
                img[r][c] = 255
                c = c - 1

    elif c_mid < 0:#左にずらす
        for r in range( r_max):
            c = 0
            while c < c_right + c_mid + 1:
                img[r][c] = img[r][c - c_mid]
                c = c + 1
        for r in range( r_max ):
            c = c_right + c_mid + 1
            print( "c:%d",c)
            while c < c_max:
                img[r][c] = 255
                c = c + 1

    #縦位置を調整する
    if r_mid > 0:#下にずらす
        for c in range( c_max ):
            r = r_max - 1
            while r > r_mid:
                img[r][c] = img[r - r_mid][c]
                r = r - 1
        for c in range( c_max ):
            r = r_mid
            while r > 0:
                img[r][c] = 255
                r = r -1
    elif r_mid < 0:#上にずらす
        for c in range( c_max ):
            r = 0
            while r < r_bottom + r_mid + 1:
                img[r][c] = img[r - r_mid][c]
                r = r + 1
        for c in range( c_max ):
            r = r_bottom + r_mid +1
            while r < r_max:
                img[r][c] = 255
                r = r + 1
    return img
"""
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
    #print( filename )

    #マーカーの読み込み
    path = os.path.join( STATIC_PATH , "marker.png" )

    marker = cv2.imread(path, 0)

    #画像ファイルの読み込みとサイズ調整
    img = cv2.imread(filename, 0)
    #imgshow( img )
    img = cv2.resize(img, (2100, 2964))

    #角度を調節する
    res_gaku = cv2.matchTemplate(img, marker, cv2.TM_CCOEFF_NORMED)
    threshold = 0.5
    loc = np.where(res_gaku >= threshold)
    #print( loc )
    min_x = min(loc[1])
    min_y = min(loc[0])
    max_x = max(loc[1])
    max_y = max(loc[0])
    print( "minx:%d,maxy:%d,miny:%d,maxy:%d"%(min_x,max_x,min_y,max_y))
    x1 = max_x - min_x
    y1 = max_y - min_y
    rad1 = math.sqrt( x1*x1 + y1*y1)
    #print(math.degrees(math.asin(y1/rad1)))
    rad = 90-math.degrees(math.asin(y1/rad1))
    print( rad )
    trans = cv2.getRotationMatrix2D((1050,1485), rad, 1.0)
    img = cv2.warpAffine(img,trans,(2100,2970))

    #img = cv2.resize(img, (1000, 1500))
    # markeと同じ画像の位置を取得する
    res_gaku = cv2.matchTemplate(img, marker, cv2.TM_CCOEFF_NORMED)
    threshold = 0.5
    loc = np.where(res_gaku >= threshold)
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
    org_id = cv2.resize(org_id,(350,100))
    test_id = cv2.resize(test_id,(350,100))
    user_id = cv2.resize(user_id,(350,100))

    o_n = ocr(org_id)
    t_n = ocr(test_id)
    u_n = ocr(user_id)

    """
    ainum = Ainum()
    #白黒チェンジ
    res , org_id = bwchange( org_id )
    o_n = ""

    imgshow( org_id )
    for c in range(4):
        o_num = org_id[10:90 , (c*42)+15:(c*42)+57]
        o_num = cv2.resize(o_num,(28,28))
        o_num = img_center( o_num )
        imgshow(o_num)
        o_n = o_n + str( ainum.get_num( o_num ) )

    res,test_id = bwchange( test_id )
    t_n = ""

    imgshow( test_id )
    for c in range(4):
        test_num = test_id[10:90 ,(c*42)+15:(c*42)+57]
        test_num = cv2.resize(test_num,(28,28))
        test_num = img_center( test_num )
        imgshow(test_num)
        t_n = t_n + str( ainum.get_num(test_num) )

    res,user_id = bwchange( user_id )

    u_n = ""

    #imgshow( user_id )
    for c in range(8):
        user_num = user_id[10:90 , (c*40)+15:(c*40)+55 ]
        user_num = cv2.resize( user_num , (28,28) )
        user_num = img_center( user_num )
        #imgshow(user_num)
        u_n = u_n + str( ainum.get_num(user_num) )
    """

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

    answer = ['ア', 'イ', 'ウ', 'エ']
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
