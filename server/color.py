import numpy as np
import math

# コメントはdocstringの記法に従う．スタイルはnumpydoc
# docstringについて https://qiita.com/simonritchie/items/49e0813508cad4876b5a
# numpydocスタイルについて https://numpydoc.readthedocs.io/en/latest/format.html#docstring-standard

class Color:
	"""
	色のRGB値を保持し，適宜他の色空間に変換したり色差を計算したりする．

	Attributes
	----------
	color : List[int]
		RGB値．[R, G, B]の順番で渡す．
	"""

	def __init__(self, color):
		"""
		Parameters
		----------
		color : List[int]
			RGB値．[R, G, B]の順番で渡す．
		"""

		self.color = color

	def __str__(self):
		return f"{self.color[0]}-{self.color[1]}-{self.color[2]}"
	
	def delta2000(self, comparison):
		"""
		自分自身にセットされた色と，比較対象の色の間の色差（CIEDE2000）を計算

		Parameters
		----------
		comparison : Color
			比較対象となる色
			同じColorクラスのデータをcomparisonとして渡す

		Returns
		----------
		delta : float
			色差の計算結果

		See Also
		--------
		rgb2lab() : RGB値をLab値に変換．（CIEDE2000の計算に必要）
		"""

		l1, a1, b1 = self.rgb2lab()
		l2, a2, b2 = comparison.rgb2lab()

		l_del_d = l2 - l1
		l_bar = (l1 + l2) / 2
		c_ast1 = math.sqrt(math.pow(a1,2)+math.pow(b1,2))
		c_ast2 = math.sqrt(math.pow(a2,2)+math.pow(b2,2))
		c_bar = (c_ast1 + c_ast2)/2

		g = (1 - math.sqrt(math.pow(c_bar,7)/(math.pow(c_bar,7) + math.pow(25,7))))*0.5

		a_d1 = a1*(1+g)
		a_d2 = a2*(1+g)
		c_d1 = math.sqrt(math.pow(a_d1,2)+math.pow(b1,2))
		c_d2 = math.sqrt(math.pow(a_d2,2)+math.pow(b2,2))
		c_bar_d = (c_d1 + c_d2)/2
		c_del_d = c_d2 - c_d1

		if b1 == a_d1:
			h_d1 = 0
		else:
			ang_h1 = self.rad2ang(math.atan2(b1,a_d1))+360
			int_h1 = ang_h1 % 360.0
			sm_h1 = ang_h1 - math.floor(ang_h1)
			h_d1 = int_h1 + sm_h1

		if b2 == a_d2:
			h_d2 = 0
		else:
			ang_h2 = self.rad2ang(math.atan2(b2,a_d2))+360
			int_h2 = ang_h2 % 360.0
			sm_h2 = ang_h2 - math.floor(ang_h2)
			h_d2 = int_h2 + sm_h2
		diff = h_d2 - h_d1

		h_del_d = 0
		if abs(diff) <= 180:
			h_del_d = diff
		elif h_d2 <= h_d1:
			h_del_d = diff + 360
  
		else:
			h_del_d = diff - 360

		H_del_d = 2 * math.sqrt(c_d1 * c_d2) * math.sin(self.ang2rad(h_del_d/2))
		H_bar_d = h_d1 + h_d2

		if abs(diff)<=180:
			H_bar_d /= 2
		elif H_bar_d < 360:
			H_bar_d = (H_bar_d + 360)/2
		else:
			H_bar_d = (H_bar_d - 360)/2

		t = 1 - 0.17*math.cos(self.ang2rad(H_bar_d - 30)) + 0.24*math.cos(self.ang2rad(2*H_bar_d)) + 0.32*math.cos(self.ang2rad(3*H_bar_d+6))  - 0.20*math.cos(self.ang2rad(4*H_bar_d-63));

		sl = 1 + 0.015 * math.pow(l_bar-50,2)/math.sqrt(20+math.pow(l_bar-50,2))
		sc = 1 + 0.045 * c_bar_d
		sh = 1 + 0.015 * c_bar_d * t

		del_the = 30 * (math.exp(-1 * math.pow((H_bar_d - 275)/25,2)))
		rc = 2 * math.sqrt(math.pow(c_bar_d,7)/(math.pow(c_bar_d,7)+math.pow(25,7)))
		rt = -1 * math.sin(self.ang2rad(2 * del_the)) * rc

		delta2000 = math.sqrt( math.pow(l_del_d/sl,2) + math.pow(c_del_d/sc,2) + math.pow(H_del_d/sh,2) + rt * c_del_d / sc * H_del_d/ sh )

		return delta2000

	def ang2rad(self, ang):
		"""
		角度をラジアンに変換します．
		"""
		return ang * math.pi /180

	def rad2ang(self, rad):
		"""
		ラジアンを角度に変換します．
		"""
		return rad * 180 / math.pi

	def rgb2lab(self):
		"""
		自分自身にセットされたRGB値をLab値に変換

		Parameters
		----------
		N/A
			selfでセットされている色を利用する
			計算に利用するだけで値を書き換えるわけではない

		Returns
		----------
		lab : List[float]
			Lab値
		"""

		x, y, z = self.rgb2xyz()
		#print("xyz:{}".format(self.rgb2xyz(linear_color)))

		xn = x / 0.95047
		yn = y / 1.00000
		zn = z / 1.08883

		l = 116 * self.func_lab(yn) - 16
		a = 500 * ( self.func_lab(xn) - self.func_lab(yn) )
		b = 200 * ( self.func_lab(yn) - self.func_lab(zn) )

		return [l, a, b]

	def func_lab(self, val):
		"""
		Lab値計算のためのヘルパー関数

		Parameters
		----------
		color : List[float]
			RGB値を正規化した値

		Returns
		----------
		result : float
			線形変換した結果
		"""
		thres = math.pow(6/29,3)
		coef = math.pow(29/3,3)
		if val > thres:
			result= math.pow(val,1/3)
		else:
			result = (coef * val + 16) / 116
		
		return result


	def rgb2xyz(self):
		"""
		自分自身にセットされたRGB値をxyz値に変換

		Parameters
		----------
		N/A
			selfでセットされている色を利用する
			計算に利用するだけで値を書き換えるわけではない

		Returns
		----------
		xyz : List[float]
			xyz値
		"""
		color_ = np.array(self.color)/255
		color_ = self.linear_exchange(color_.tolist())
		matrix = [
		[0.4124, 0.3576, 0.1805],
		[0.2126, 0.7152, 0.0722],
		[0.0193, 0.1192, 0.9505]
		]

		matrix_np_array = np.array(matrix)
		color_np_array = np.array(color_)

		return (matrix_np_array @ color_np_array).tolist()

	def linear_exchange(self, color):
		"""
		xyz値計算のためのヘルパー関数

		Parameters
		----------
		color : List[float]
			RGB値を正規化した値

		Returns
		----------
		result : float
			線形変換した結果
		"""
		result = [0,0,0]
		for i in range(0,3):
			if(color[i] <= 0.04045):
				result[i] = color[i] / 12.92
			else:
				result[i] = math.pow( (color[i] + 0.055) / 1.055, 2.4)
		
		return result

	def rgb2hsv(self):
		"""
		自分自身にセットされたRGB値をHSV値に変換

		Parameters
		----------
		N/A
			selfでセットされている色を利用する
			計算に利用するだけで値を書き換えるわけではない

		Returns
		----------
		hsv : List[float]
			HSV値
		"""
		r,g,b = map(lambda x:x/255,self.color)
		_max = max(r,g,b)
		_min = min(r,g,b)

		if _max != 0:
			s = ( (_max - _min) / _max ) * 100
		else:
			s = 0
			
		v = _max * 100
	
		if (_max - _min) == 0:
			h = 0
			return [h,s,v]

		if _max == r:
			h = 60 * ( (g-b) / (_max - _min) )
		elif _max == g:
			h = 60 * ( (b-r) / (_max - _min) ) + 120
		elif _max == b:
			h = 60 * ( (r-g) / (_max - _min) ) + 240
		elif _min == _max:
			h = 0
		if h < 0:
			h += 360
		
		h = h % 360

		return [h,s,v]
	
	def getColorCode(self):
		r, g, b = self.color
		print(f"{r},{g},{b}")
		return f"#{r:02x}{g:02x}{b:02x}"