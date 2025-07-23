import os
import sys
import cv2
import numpy as np
import math
from statistics import median, mean
from pathlib import Path

class Filter():
    def __init__(self, chroma=100, value=100, alpha=0.7, tile=40, grid=20):
        # 彩度と明度
        self.chroma = chroma
        self.value = value

        # 画像とフィルターの合成比率 base : grad = 1-alpha : alpha
        self.alpha=alpha

        #タイル数
        self.tile=tile

        #グリッド状に分割する際のサイズ(n✕n)
        self.grid=grid
        print(f"""\
[filter settings]
- chroma={self.chroma},
- value={self.value},
- alpha={self.alpha},
- tile={self.tile},
- grid={self.grid}""")

    """
    bgr2hsv()
    BGRからHSVに変換
    h = 0 ~ 359
    s,v = 0 ~ 100
    """
    def bgr2hsv(self, bgr):
        # b,g,r = bgr
        b,g,r = map(lambda x:x/255,bgr)
        _max = max(b,g,r)
        _min = min(b,g,r)
        
        if _min == _max:
            h = 0
        elif _max == r:
            h = 60 * ( (g-b) / (_max - _min) )
        elif _max == g:
            h = 60 * ( (b-r) / (_max - _min) ) + 120
        elif _max == b:
            h = 60 * ( (r-g) / (_max - _min) ) + 240
        
        if h < 0:
            h += 360
        h = h % 360
        if _max != 0:
            s = ( (_max - _min) / _max ) * 100
        else:
            s = 0
        v = _max * 100
        return np.array([h,s,v])

    """
    hsv2bgr()
    h = 0 ~ 359
    s,v = 0 ~ 100
    """
    def hsv2bgr(self, hsv):
        #h = 0-360
        #s,v = 0-100
        h,s,v = hsv
        s /= 100
        v /= 100
        if s == 0:
            r,g,b = v*255
            return np.array([b,g,r],dtype=np.uint8)

        dh = math.floor(h/60)
        p = v * (1 - s)
        q = v * (1 - s * (h / 60 - dh))
        t = v * (1 - s * (1 - (h / 60 - dh)))

        if dh == 0:
            r,g,b = v,t,p
        elif dh == 1:
            r,g,b = q,v,p
        elif dh == 2:
            r,g,b = p,v,t
        elif dh == 3:
            r,g,b = p,q,v
        elif dh == 4:
            r,g,b = t,p,v
        elif dh == 5:
            r,g,b = v,p,q

        r,g,b = map(lambda num:(num*255),[r,g,b])
        return np.array([b,g,r],dtype=np.uint8)

    """
    getGradSub()
    指定した色から色に変化する配列を作成する
    R,G,Bを別々に受け取って変化させる
    start = 0~255の値
    stop  = 0~255の値
    row   = 画像の縦幅
    column= 画像の横幅
    """
    def getGradSub(self, start, stop, row, column):
        return np.tile(np.linspace(start, stop, column), (row, 1))

    """
    getGrad()
    getGradSub()を使って作成した配列をマージして１つの配列にしたものを返す（画像の生成）
    cv2.imwrite()で画像を保存するため、RGBをBGRに変換してreturnしている
    返り値 = ndarray画像
    start_list = RGBリスト
    mid_list = RGBリスト
    stop_list = RGBリスト
    row = 画像の縦幅
    column = 画像の横幅
    """

    def getGrad(self, color, row=300, column=300):
        start_list = color[0]
        stop_list = color[1]
        result = np.zeros((row, column, len(start_list)), dtype=np.float64)

        for idx, (start, stop) in enumerate(zip(start_list,  stop_list)):
            result[:,0:column//2,idx] = self.getGradSub(start, 255, row, column//2)
            result[:,column//2:column,idx] = self.getGradSub(255, stop, row, column//2)

            # result[:,0:column,idx] = self.getGradSub(start, stop, row, column)

        return np.uint8(result), row, column

    def concat_tile(self, im_list_2d):
            return cv2.vconcat([cv2.hconcat(im_list_h) for im_list_h in im_list_2d])

    """
    getGradTile()
    getGrad()を使って作成したグラディエーション画像を3*3のタイルの画像として保存
    """
    def getGradTile(self, grad, row, column):
        tile=self.tile
        width=row//tile
        height=column//tile

        grad = cv2.resize(grad,(width, height))
        grad2 = cv2.rotate(grad,cv2.ROTATE_90_CLOCKWISE) # 時計回りに90度回転

        cnt=0
        tmp2=[]
        #偶数タイルの場合
        if tile%2==0:
            for i in range(tile):
                tmp=[]
                if i%2==0:
                    for j in range(tile):
                        if cnt%2==0:
                            tmp.append(grad)
                        else:
                            tmp.append(grad2)
                        cnt+=1
                    tmp2.append(tmp)
                else:
                    for j in range(tile):
                        if cnt%2==0:
                            tmp.append(grad2)
                        else:
                            tmp.append(grad)
                        cnt+=1
                    tmp2.append(tmp)

        #奇数タイルの場合
        else:
            for i in range(tile):
                tmp=[]
                for j in range(tile):
                    if cnt%2==0:
                        tmp.append(grad)
                    else:
                        tmp.append(grad2)
                    cnt+=1
                tmp2.append(tmp)

        result = self.concat_tile(tmp2)
        result = cv2.resize(result,(row, column))
        return np.uint8(result)
    """
    blendImage()
    ベースになる画像とフィルター画像をブレンドする
    base = ベース画像
    grad = フィルター画像
    """
    def blendImage(self, base, grad):
        height = base.shape[0]
        width = base.shape[1]
        # if width < height: # 横より縦が大きいなら
        #     grad = cv2.rotate(grad,cv2.ROTATE_90_CLOCKWISE) # 時計回りに90度回転
        grad = cv2.resize(grad,(width,height))
        result = cv2.addWeighted(base,1-self.alpha,grad,self.alpha,0)

        return result


    """
    getAvgColor()
    画像全体の色の平均を求める
    """
    def getAvgColor(self, img):
        # img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB) # bgrをrgbに変換
        avg_color_per_row = np.average(img,axis=0) # 行ごとの平均色
        avg_color = np.average(avg_color_per_row,axis=0) # 画像全体の平均色(BGR)
        return avg_color


    """
    getColor()
    画像を3分割したとき、最もグレーの部分が少ない区画を元にグラデーション画像に使う色を決定する
    """

    def getColor(self, img):
        grid=self.grid
        hue_list = np.zeros((grid*grid)) 
        red=[]
        green=[]
        blue=[]
        
        #画像をグリッド状に分割
        split_images = []
        for row_img in np.array_split(img, grid, axis=0):
            for chunk in np.array_split(row_img, grid, axis=1):
                split_images.append(chunk)


        # #分割した画像の平均画素値を取得
        for idx, split_img in enumerate(split_images):  
            hsv=self.bgr2hsv(self.getAvgColor(split_img))
            h, s, v = hsv
            hue_list[idx] = h

        
        #平均画素値をr, g, bに分類
        for s in range(len(hue_list)):
            if 0 <= hue_list[s] < 60 or 300 <= hue_list[s]< 360:
                red.append(hue_list[s]) 
            elif 60 <=  hue_list[s] < 180:
                green.append(hue_list[s])
            elif 180 <= hue_list[s] < 300:
                blue.append(hue_list[s])
        
        #色区画(red, green, blue)のうち、要素数の多い2つのリストの中央値を取得
        tmp=[red, green, blue]
        tmp.remove(min(tmp))
        h1=mean(tmp[0])


        flg = "0"
        #red, green, blueどれか一つにしか値が入ってない場合
        if len(tmp[1]) == 0:
            h2=(h1+90)%360
            flg="1"
        else :
            h2=mean(tmp[1])

        
        #h1とh2の値が近いとき
        # if abs(h1-h2) < 60:
        #     h2=(h1+90)%360
        #     flg="2"


        #補色リストを作成
        grad_color = []
        s = self.chroma
        v = self.value
        grad_color.append(self.hsv2bgr([(h1+180)%360,s,v]))
        grad_color.append(self.hsv2bgr([(h2+180)%360,s,v]))
        
        return grad_color, flg

    def getCAPTCHAImage(self, img_file_path, out_dir_path="./"):
        # base画像のロード
        base_img = cv2.imread(str(img_file_path))
        # gradの生成に使う色を取得
        # flg = "0"
        color, flg = self.getColor(base_img)
        # if flg == "1":
        #     print(f"only-one-section {idx+1}")
        # if flg == "2":
        #     print(f"mono {idx+1}")
        # grad画像の作成
        grad_img, row, column = self.getGrad(color)
        #grad画像を用いてタイル画像の作成--------NEW!!!
        grad_tile_img = self.getGradTile(grad_img, row, column)

        result_img = self.blendImage(base_img, grad_tile_img)
        
        base_path = Path(out_dir_path)

        # grad画像のファイルパス
        grad_name = f"{img_file_path.stem}_grad.jpg"
        grad_path = base_path.joinpath(grad_name)
        cv2.imwrite(str(grad_path), grad_tile_img)

        # result画像のファイルパス
        result_name = f"{img_file_path.stem}_result.jpg"
        result_path = base_path.joinpath(result_name)
        cv2.imwrite(str(result_path), result_img)

        return result_path

    def createCAPTCHAImage(self, img_file_path, out_dir_path="./"):
        # base画像のロード
        base_img = cv2.imread(str(img_file_path))
        # gradの生成に使う色を取得
        # flg = "0"
        color, flg = self.getColor(base_img)
        # if flg == "1":
        #     print(f"only-one-section {idx+1}")
        # if flg == "2":
        #     print(f"mono {idx+1}")
        # grad画像の作成
        grad_img, row, column = self.getGrad(color)
        #grad画像を用いてタイル画像の作成--------NEW!!!
        grad_tile_img = self.getGradTile(grad_img, row, column)

        result_img = self.blendImage(base_img, grad_tile_img)

        base_path = Path(out_dir_path)

        # grad画像のファイルパス
        grad_name = f"{img_file_path.stem}_grad.jpg"
        grad_path = base_path.joinpath(grad_name)
        cv2.imwrite(str(grad_path), grad_tile_img)

        # result画像のファイルパス
        result_name = f"{img_file_path.stem}_result.jpg"
        result_path = base_path.joinpath(result_name)
        cv2.imwrite(str(result_path), result_img)

import sys
if __name__ == "__main__":
    file_name = sys.argv[1]
    fil = Filter()
    fil.createCAPTCHAImage(Path(file_name))