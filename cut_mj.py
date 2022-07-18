#問題を切り取るプログラム
import cv2
import math
import numpy as np
from PIL import Image
import os , sys
import csv

#pilで読込cv2に吐き出す
def pilread(file_path):
    img = Image.open( file_path )
    return np.asarray( img )

#numpyで渡して画像保存する。
def pilwrite( numpy_image , file_path ):
    img = Image.fromarray(np.uint8(numpy_image))
    img.save( file_path )

# img_in( directory path) , img_out( directory path )  , file_name 'feh29h'
def cut_mondai(img_in , img_out , file_name , freq=2 ):
    img_no = 1
    for f in os.listdir( img_in ):
        #img = cv2.imread()
        img = pilread( "%s/%s"%(img_in,f) )
        img = cv2.resize(img,(920,1300))
        img = img[20:1220,20:900]
        #サイズを変更する
        img2 = img

        #img2を2値化
        img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
        thresh = 100
        max_pixel = 250
        ret, img2 = cv2.threshold(img2, thresh, max_pixel, cv2.THRESH_BINARY)

        #特徴量を取得する
        #detector = cv2.ORB_create()
        detector = cv2.AgastFeatureDetector_create()
        #detector = cv2.FastFeatureDetector_create()

        #特徴量のkeyを取得する
        keypoints = detector.detect(img2)
        
        #ノイズを消去する
        #keypoints = noize_cut(keypoints,900,1280, freq )

        #x,yの配列
        px = []
        py = []
        for key in keypoints:
            px.append( key.pt[0])
            py.append( key.pt[1] )
        #print( py )
        #xの最小値と最大値を取得
        max_x = math.floor( max(px) )
        min_x = math.floor( min(px) )


        #keyの高さの間隔を取得
        interval = []
        spt = py[0]
        old_y = py[0]
        for y in py:
            dy = y - old_y
            print( dy )
            if dy > 30:
                interval.append((math.floor(spt), math.floor(old_y)))
                spt = y
            old_y = y

        if old_y - spt > 50:
            interval.append((math.floor(spt), math.floor(old_y)))

        #for m in interval:
        #    print( m )

        out = img

        #特徴をマークする
        #out = cv2.drawKeypoints(img2,keypoints,None)

        #showimage( out )

        for dect in interval:
            #out = cv2.rectangle(out,(min_x, y1 ),(max_x, dect[0]),(0,0,0),2)
            path = img_out+"/%s"
            if img_no < 10:
                path = path%"%s0%s.png"%(file_name,img_no)
            else:
                path = path % "%s%s.png"%(file_name,img_no)

            #ファイルを保存する
            # cv2.imwrite(path,out[dect[0]-15:dect[1]+15,min_x-15:max_x+15])
            pilwrite(out[dect[0]-15:dect[1]+15,min_x-15:max_x+15],path)
            img_no = img_no + 1

        #print( str(img_no - 1) + "問")


# img_in( directory path) , img_out( directory path )  , file_name 'feh29h'
# 余白を削除するのみ
def cut_mondai_margin(img_in ,img_out, freq=2 ):
    for i,f in enumerate(os.listdir( img_in )):
        if ".png" in f:
            # img = cv2.imread("%s/%s"%(img_in,f))
            img = pilread( "%s/%s"%(img_in,f) )
            print("%s/%s"%(img_in,f))
            #showimage( img )
            # 特徴量抽出
            #img2 = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            thresh = 100
            max_pixel = 250
            ret, img3 = cv2.threshold(img, thresh, max_pixel, cv2.THRESH_BINARY)

            #特徴量を取得する
            #detector = cv2.ORB_create()
            detector = cv2.AgastFeatureDetector_create()
            #detector = cv2.FastFeatureDetector_create()

            #特徴量のkeyを取得する
            keypoints = detector.detect(img3)

            #ノイズを消去する
            keypoints = noize_cut(keypoints,img3.shape[1],img3.shape[0], freq )

            #x,yの配列
            px = []
            py = []
            for key in keypoints:
                px.append( key.pt[0])
                py.append( key.pt[1] )

            #xの最小値と最大値を取得
            max_x = math.floor( max(px) ) + 20
            min_x = math.floor( min(px) ) - 20
            max_y = math.floor( max(py) ) + 20
            min_y = math.floor( min(py) ) - 20

            # ファイルネーム
            if i < 10:
                filename = "%s/%s.png" % (img_out, f[0:len(f)-4].replace("-","_") )
            else:
                filename = "%s/%s.png" % (img_out, f[0:len(f)-4].replace("-","_") )

            # cv2.imwrite(filename, img[min_y:max_y , min_x:max_x])
            pilwrite( img[min_y:max_y,min_x:max_x] , filename )
            # os.remove( "%s/%s"%(img_in,f) )

# 画像を2値化
def conv_binary(img):
    img_gry = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = 100
    max_pixel = 250
    ret, img_gry = cv2.threshold(img_gry, thresh, max_pixel, cv2.THRESH_BINARY)
    return img_gry

# 画像をグレーアウト
def conv_gray(img):
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return img_gray

#特徴量で切り取る
def tokucyou_cut(img , freq=2 ):
    # img1を2値化
    img_gry = conv_binary( img )
    # 特徴量を取得する
    # detector = cv2.ORB_create()
    detector = cv2.AgastFeatureDetector_create()
    # detector = cv2.FastFeatureDetector_create()

    # 特徴量のkeyを取得する
    kp = detector.detect(img_gry)
    # ノイズを消去する
    kp = noize_cut(kp, 1080, 1590, freq)

    # 特徴をマークする
    #out = cv2.drawKeypoints(img,kp,None)
    #cv2.imwrite("cut_image/t.png",out)
    #showimage(out)
    if len(kp) > 0:
        # x,yの配列
        px = []
        py = []
        for key in kp:
            px.append(key.pt[0])
            py.append(key.pt[1])

        # xの最小値と最大値を取得
        max_x = math.floor(max(px))
        min_x = math.floor(min(px))
        max_y = math.floor(max(py))
        min_y = math.floor(min(py))

        #showimage(img[min_y-15:max_y+15,min_x-15:max_x+15])
        rect = (min_x,max_x,min_y,max_y)
        return img[min_y-30:max_y+30,min_x-30:max_x+30],rect
    else:
        return img_gry,()
# PILをCV2
def pil2cv(image):
    ''' PIL型 -> OpenCV型 '''
    new_image = np.array(image, dtype=np.uint8)
    if new_image.ndim == 2:  # モノクロ
        pass
    elif new_image.shape[2] == 3:  # カラー
        new_image = cv2.cvtColor(new_image, cv2.COLOR_RGB2BGR)
    elif new_image.shape[2] == 4:  # 透過
        new_image = cv2.cvtColor(new_image, cv2.COLOR_RGBA2BGRA)
    return new_image

# 画像同士の類似度
def cv2MatchTemplate2(image , marker ):
    res = cv2.matchTemplate(image, marker, cv2.TM_CCOEFF_NORMED)
    minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(res)
    #loc = np.where(res >= threshold)
    return {'minVal':minVal,'maxVal':maxVal,'minLoc':minLoc,'maxLoc':maxLoc}

# 画像同士の類似度
def cv2MatchTemplate(image , marker,threshold ):
    res = cv2.matchTemplate(image, marker, cv2.TM_CCOEFF_NORMED)
    minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(res)
    loc = np.where(res >= threshold)
    return loc,maxVal

def check( m , x ,y ):
    i = 0
    while i < len( m ):
        list = m[i]
        if list[0] == x and list[1] == y:
            return i
        i = i + 1
    return -1

def noize_cut( keypoints ,x_size , y_size ,power ):
    maplist = []
    # [ [ x , y , [ key ]] , [ x, y , [ key ,key ] ]
    for key in keypoints:
        x = math.floor( key.pt[0] / 15)
        y = math.floor( key.pt[1] / 15)
        i = check( maplist,x,y)
        if i >= 0:
            maplist[i][2].append( key )
        else:
            list = []
            list.append(x)
            list.append(y)
            keys = []
            keys.append( key )
            list.append(keys)
            maplist.append(list)

    for list in maplist:
        if len(list[2]) < power:
            for key in list[2]:
                keypoints.remove( key )

    return keypoints

def showimage(img):
    cv2.imshow('Image', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def main():
    cut_mondai_hj(img_in='C:\\Users\\mnt\\Desktop\\png',img_out='C:\\Users\\mnt\\Desktop\\png_cut',file_name='148')

if __name__ == '__main__':
    main()