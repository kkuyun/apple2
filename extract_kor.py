from moviepy import AudioFileClip
import math
import numpy as np
import shutil
import os
import time
import pygame
import cv2
import base64
import json
# 겁나 많은 라이브러리들... 나중에 줄여야할듯


# & C:/Users/Yun/AppData/Local/Programs/Python/Python312/python.exe c:/Users/Yun/Documents/GitHub/apple/pixelextract3.py 테스트 실행용
# pyinstaller -F extract_kor.py

# 이 밑으로 인터넷 검색으로 찾은 고마운 함수들


def makedir(directory_path):
    if not os.path.exists(directory_path):
            os.makedirs(directory_path)
        
def deletefolder(directory_path):
    if os.path.exists(directory_path) and os.path.isdir(directory_path):
        shutil.rmtree(directory_path)
        print(f"폴더 '{directory_path}' 와 내용물을 제거했습니다.")
    else:
        print(f"폴더 '{directory_path}' 가 존재하지 않거나 폴더가 아닙니다.")
        
def is_number(s):
    """ 숫자일시 True 반환. """
    try:
        float(s)
        return True
    except ValueError:
        return False

# 함수 끝

ASCII = " .'`^,:;Il!i><~+_-?][}{1)(|tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B$@" 

mag = 1
comprate = 0
extype = "0" # 숫자로 하는 게 융통성 있겠지만 input은 문자열로 받으니깐 이게 편해


# 메인 함수
def extract_frames(Tdirectory_path, path): # 추출하는 부분, 사실상 이 함수가 다 함
    Greylist = []

    imgcount = 1
    cap = cv2.VideoCapture(path)
    imgnum = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    framecount = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    while cap.isOpened(): # 추출 시작
        ret, img = cap.read()
        if not ret:
            break  # 영상 끝
        
        if imgcount % 100 == 0:
            print(f"프레임 추출 중: {imgnum}/{imgcount}")
        img = img[::mag, ::mag] # 이 부분이랑 numpy 쓰는 부분들 대충 반복문으로 때우려다가 겁나 렉걸려서 결국 AI 도움 받고 다시 했다

        if extype == "1": # ASCII로 추출
            Grey = (img @ [0.114, 0.587, 0.299]).astype(np.uint8) # 네이버 블로그에서 찾은 색상의 밝기를 구하는 공식 사용
            Grey = np.clip(Grey // math.floor(255/len(ASCII)), 0, len(ASCII)-1)

            char_array = np.array(list(ASCII))
            Grey = char_array[Grey]
            Grey = '\n'.join(' '.join(row) for row in Grey)

            Greylist.append(Grey)
            if imgcount % comprate == 0 or imgcount == framecount:
                with open(f"{Tdirectory_path}frame{(imgcount - 1)//comprate + 1}.txt", "a", encoding="utf-8") as f:
                    f.truncate(0)
                    f.write(json.dumps(Greylist))
                Greylist = []

        else:
            if extype == "2": # 리사이즈 부분
                img = cv2.resize(img, (WIDTH, HEIGHT), interpolation=cv2.INTER_AREA) # 리사이즈는 사실 계획엔 없었지만 AI가 추천해서 결국 넣었다
            flat = img.reshape(-1, 3)
            with open(f"{Tdirectory_path}frame{(imgcount - 1)//comprate + 1}.txt", "a", encoding="utf-8") as f:
                f.write(base64.b64encode(flat.tobytes()).decode("utf-8"))


        imgcount += 1
    cap.release() # 추출 완료

def extract_audio(path, length=390):
    for i in os.listdir('.'):
        if i[:len(path)-4] == path[:len(path)-4] and i[-4:] == ".mp3":
            os.remove(i)
    
    audio = AudioFileClip(path)
    audio.write_audiofile(f"{path[:len(path)-4]}_original.mp3")

    duration = audio.duration
    segment_count = math.ceil(duration/length)

    for i in range(segment_count):
        start_time = i*length
        end_time = min((i + 1) * length, duration)
        segment = audio.subclipped(start_time, end_time)
        segment.write_audiofile(f"{path[:len(path)-4]}_segment{i+1}.mp3")
    

while True:
    print("영상 파일명을 입력해주십시오. (.mp4 확장자 부분 제외)")
    videoname = input("문자 : ")

    if os.path.exists(videoname + ".mp4"):
        while True:
            videopath = videoname + ".mp4"
            framedir = videopath[:len(videopath)-4] + "_frames"
            convertdir = 'converted/'

            cap = cv2.VideoCapture(videopath)
            WIDTH = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            HEIGHT = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            FPS = cap.get(cv2.CAP_PROP_FPS)
            FRAME_COUNT = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            # 이 밑으로 입력을 받기 위한 반복문 및 if문 지옥
            print("1: 추출, 2: 출력 (ASCII 출력 후 시험용)")
            what = input("숫자 : ")
            if what == "1":
                print("추출 선택됨")

                while True:
                    print("추출 형식을 골라주십시오.")
                    print("ASCII: 1, 픽셀: 2")
                    extype = input("숫자 : ")
                    if extype == "1":
                        print("ASCII 선택됨")
                        break
                    elif extype == "2":
                        print("픽셀 선택됨")
                        while True:
                            print("해상도 압축 형식을 골라주십시오.")
                            print("해상도 재할당: 1, 축소 비율: 2")
                            extype = input("숫자 : ")
                            if extype == "1":
                                print("재할당 선택됨")
                                extype = "2"

                                while True:
                                    print("새 너비를 입력해주십시오. (최대: 1000)")
                                    WIDTH = input("숫자 : ")
                                    if is_number(WIDTH):
                                        WIDTH = int(WIDTH)
                                        if WIDTH > 1000:
                                            print("1000 이하의 숫자를 입력해주십시오.")
                                        elif WIDTH <= 0:
                                            print("양수를 입력해주십시오.")
                                        else:
                                            break
                                    else:
                                        print("숫자를 입력해주십시오.")
                                
                                while True:
                                    print("새 높이를 입력해주십시오. (최대: 1000)")
                                    HEIGHT = input("숫자 : ")
                                    if is_number(HEIGHT):
                                        HEIGHT = int(HEIGHT)
                                        if HEIGHT > 1000:
                                            print("1000 이하의 숫자를 입력해주십시오.")
                                        elif HEIGHT <= 0:
                                            print("양수를 입력해주십시오.")
                                        else:
                                            break
                                    else:
                                        print("숫자를 입력해주십시오.")
                                break

                            elif extype == "2":
                                print("축소 선택됨")
                                extype = "3"
                                break  
                            else:
                                print("보기에 있는 숫자를 입력해주십시오.")
                            
                        break
                        
                    else:
                        print("보기에 있는 숫자를 입력해주십시오.")

                while True:
                    mag = 1
                    rates = []
                    for i in range(10000):
                        if WIDTH % (i + 1) == 0 and HEIGHT % (i + 1) == 0:
                            rates.append(i+1)


                    if extype != "2":
                        while True:
                            print(f"사용 가능한 비율: 1분의 {rates}")
                            
                            mag = input("숫자 : ")
                            if is_number(mag):
                                mag = int(mag)
                                if (mag > 0 and mag in rates):
                                    mag = mag
                                    print(f"비율 1/{mag} 선택됨")
                                    break
                                else:
                                    print("보기에 있는 비율을 입력해주십시오.")
                            else:
                                print("숫자를 입력해주십시오.")

                    
                    cancelinput = "?"
                    if (WIDTH/mag) * (HEIGHT/mag) > 16384 and extype == "1": # 16384는 textlabel의 글자 제한
                        print("경고: 추출물의 텍스트가 너무 깁니다, 로블록스에서 재생시 잘릴 수 있습니다. 다시 고르시겠습니까?")
                        while True:
                            cancelinput = input("Y/N : ")
                            if cancelinput == "Y" or cancelinput == "y" or cancelinput == "N" or cancelinput == "n":
                                break
                            else:
                                print("잘못된 입력입니다, Y 또는 N 을 입력해주십시오. : ")
                    if cancelinput == "Y" or cancelinput == "y":
                        continue

                    break


                comprate = math.ceil(FRAME_COUNT/250) # 깃허브 데스크탑으로 한번에 올릴 수 있는 파일 개수는 300개 위 아래인것 같다.
                # 원래 몇 프레임마다 파일 하나로 만들지 고를 수 있었지만 파일이 몇개가 될지랑 파일 크기를 직접 고려해야해서 대충 250개 고정. 대신 업로드가 좀 느리다. 용량은 같다.
                if os.path.exists(videopath[:len(videopath)-5] + ".mp3"):
                    os.remove(videopath[:len(videopath)-5] + ".mp3")

                deletefolder(framedir)

                makedir(framedir)

                with open(f"{framedir}/Preference.txt", "a", encoding="utf-8") as f:
                    f.truncate(0)
                    f.write(f'[{WIDTH}, {HEIGHT}, {mag}, {FRAME_COUNT/FPS}, {FRAME_COUNT}, {comprate}, "{extype}"]')

                extract_audio(videopath)

                extract_frames(framedir +"/", videopath)

            elif what == "2": # ASCII 추출물을 출력하는 부분, 대충 만들어서 출력시 터미널에 다 담기지 않을 때가 많다.
                if os.path.exists(f"{framedir}/Preference.txt"):
                    print("출력 선택됨")

                    Preference = []
                    with open(f"{framedir}/Preference.txt", "r", encoding="utf-8") as f:
                        Preference = json.loads(f.read())
                    if Preference[6] == "1":

                        pygame.mixer.init()
                        try:
                            pygame.mixer.music.load(videopath[:len(videopath)-4] + ".mp3")
                            pygame.mixer.music.set_volume(.25)
                        except:
                            print(f"{videopath[:len(videopath)-4] + ".mp3"} 를 찾지 못했습니다.")


                        b = []

                        framenum = 1
                        framecount = Preference[4]//Preference[5]
                        if Preference[4]%Preference[5] > 0:
                            framecount+=1

                        while framenum < framecount:
                            if framenum % 100 == 0:
                                print(f"{framecount}/{framenum}")
                            with open(f"{framedir}/frame{framenum}.txt", "r", encoding="utf-8") as f:
                                b.extend(json.loads(f.read()))
                            framenum+=1

                        basetime = time.time()
                        pygame.mixer.music.play()
                        framenum = 1
                        while framenum < FRAME_COUNT:
                            time.sleep(1/FPS)
                            try:
                                print(b[framenum - 1])
                            except:
                                print("출력 끝")
                                break
                            int(FRAME_COUNT / (FRAME_COUNT/FPS) * (time.time() - basetime))
                            framenum = int(FRAME_COUNT / (FRAME_COUNT/FPS) * (time.time() - basetime))
                    else:
                        print("추출 형식이 ASCII가 아닙니다.")
                else:
                    print("추출물을 찾지 못했습니다.")
            else:
                print("보기에 있는 숫자를 입력해주십시오.")
    else:
        print("영상이 발견되지 않았습니다. 다시 입력해주십시오.")

