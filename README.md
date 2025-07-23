# C2CAPTCHA-Usability
A CAPTCHA (Completely Automated Public Turing test to tell Computers and Humans Apart) that tries to distinguish between humans and bots by applying on color constancy, which is difficult to reproduce by machines.

This repository presents a two types of Color Constancy CAPTCHAs (C2CAPTCHA).
Note that this api server is used for experimental purpose.

# Notice
This project was developed for the experiments in the following paper.
## Bibtex
```
@article{Shotaro Usuzaki20242024XBL0052,
  title={Usability improvement in color constancy CAPTCHA},
  author={Shotaro Usuzaki and Wang Yihan and Kentaro Aburada and Hisaaki Yamaba and Kayoko Takatsuka and Tetsuro Katayama and Mirang Park and Naonobu Okazaki},
  journal={IEICE Communications Express},
  volume={13},
  number={8},
  pages={331-334},
  year={2024},
  doi={10.23919/comex.2024XBL0052}
}
```

# Dependencies
- Python 3.10

# Getting Started
```
$ git clone https://github.com/hexamp/c2captcha-usability.git

$ cd c2captcha-usability

$ python -m vevn venv

$ source ./venv/bin/activate

$ (venv) python -m pip install -r requrements.txt
```

# How to Use
## Create Challenges
- Put the challenge folder that is consisted of `answers` and `images`
- In `answers`, you can put the original base image and corresponding correct answer `answer.json`.
- In `images`, you can put the plane images what you want to present as the CAPTCHA image.
- In `settings.yaml`, you can change the parameter of color filter. 
## Activate Proposed CAPTCHA Server
```
$ cd server
$ uvicorn proposed_captcha:app --port=8080
```
- You can try the proposed CAPTCHA to open `html/captcha_location.html`
## Activate Previous CAPTCHA Server
```
$ cd server
$ uvicorn previous_captcha:app --port=8081
```
- You can try the proposed CAPTCHA to open `html/captcha_color.html`

