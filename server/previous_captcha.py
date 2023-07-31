from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

import numpy as np
import color
import uuid
import datetime
import cv2
import pathlib
import random
import json
from base64 import b64encode

app = FastAPI()

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["POST"],
	allow_headers=["*"]
)

class Data(BaseModel):
	uuid : str
	color : List[int]
	position : List[int]


class CAPTCHA_Server():
	def __init__(self, challenge_dir="./challenges/challenge_origin/"):
		dir = pathlib.Path(challenge_dir)
		self.captcha_image_dir = dir.joinpath("images")
		self.captcha_images = list(self.captcha_image_dir.iterdir())
		random.shuffle(self.captcha_images)
		self.captcha_mapping = {}
		self.captcha_answer_dir = dir.joinpath("answers")
		self.captcha_result_dir = dir.joinpath("previous","results")
		if not self.captcha_result_dir.exists():
			self.captcha_result_dir.mkdir(parents=True)
		self.image_ext = "jpg"
		self.answer_dict = self.getAnswerDict(self.captcha_answer_dir)

	def sendChallenge(self):
		img_path = self.captcha_images.pop()
		if len(self.captcha_images) == 0:
			self.captcha_images = list(self.captcha_image_dir.iterdir())
			random.shuffle(self.captcha_images)
		with open(str(img_path), 'rb') as f:
			blob_data = b64encode(f.read())
			captcha_id = str(uuid.uuid4())
			img_name = img_path.name
			answer_color = self.getAnswerColor(img_name)
			self.captcha_mapping[captcha_id] = (datetime.datetime.now(), img_name, str(img_path), answer_color)
			position = self.answer_dict[str(img_path.name)]

			return { "uuid" : captcha_id, 
					"blob" : blob_data.decode('utf-8'),
					"img_num" : img_name,
					"position" : position
                    }
		
	def validateResponse(self, data:Data):
		if data.uuid not in self.captcha_mapping:
			return {"result" : "99.999"}
	
		(timestamp, img_name, img_path, answer_color) = self.captcha_mapping.pop(data.uuid)
		current_time = datetime.datetime.now()
		diff = current_time - timestamp
		challenge_id = img_name
		
		if diff.seconds > 60.0:
			return {"result" : "99.999"}
		
		estimate_color = color.Color(data.color)
		delta = self.validateAnswer(estimate_color, answer_color)
		result_file = str(self.captcha_result_dir.joinpath(f"{data.uuid}"))
		self.recordResult(result_file, img_path, challenge_id, (estimate_color, answer_color), data, delta, diff.total_seconds())
		return {"result" : delta}
	
	def validateAnswer(self, response: color.Color, answer: color.Color):
		return response.delta2000(answer)

	def recordResult(self, file_name:str, img_path:str, challenge_id:int, color_tuple: tuple[color.Color], data:Data, result:float, timediff:float):
		with open(file_name, "w") as f:
			f.write("file_path,estimate_color,position,answer_color,delta,time\n")
			file_path = challenge_id
			e_color, a_color = color_tuple
			estimate_color_str = str(e_color)
			answer_color_str = str(a_color)
			position_str = "-".join(map(str,data.position))

			delta_str = f"{result:.3f}"
			f.write(f"{file_path},{estimate_color_str},{position_str},{answer_color_str},{delta_str},{str(timediff)}\n")

	def getAnswerColor(self, img_name):
		w=5
		h=5
		answer_img_name = str(self.captcha_answer_dir.joinpath(f"{img_name}"))

		answer_img = cv2.imread(answer_img_name)
		answer_img = cv2.cvtColor(answer_img, cv2.COLOR_BGR2RGB)
		x1, y1, x2, y2 = self.answer_dict[img_name]
		c_x = (x1+x2)//2
		c_y = (y1+y2)//2
		avg = np.mean(answer_img[c_y-h:c_y+h, c_x-w:c_x+w], axis=0)
		avg = np.mean(avg, axis=0)
		r, g, b = avg.astype(int)
		answer_color = color.Color([r,g,b])
		return answer_color

	def getAnswerDict(self, path: pathlib.Path):
		answer_json = str(path.joinpath("answer.json"))
		return json.load(open(answer_json, 'r'))

C2CAPTCHA_SERVER = CAPTCHA_Server(challenge_dir="./challenges/challenge_example/") #example
 
@app.post("/challenge")
async def captcha_challenge():
	return C2CAPTCHA_SERVER.sendChallenge()


@app.post("/response")
async def captcha_response(data: Data):
	return C2CAPTCHA_SERVER.validateResponse(data)

