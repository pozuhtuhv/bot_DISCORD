import os
from dotenv import load_dotenv
import json

# .env 파일 활성화
load_dotenv()
TOKEN = os.getenv('TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')
VOICE_CHANNEL_ID = os.getenv('VOICE_CHANNEL_ID')
VOICE_TEXTCHANNEL_ID = os.getenv('VOICE_TEXTCHANNEL_ID')
ADMIN_ID = os.getenv('ADMIN_ID')
STAFF_ROLE = "Admin"
BUS_KEY = os.getenv('BUS_KEY')

import requests
import json

"""
Base : 창원버스정보시스템
URL : https://bus.changwon.go.kr/
"""

"""
100번 일반형버스의 위치정보를 검색할 경우
- http://openapi.changwon.go.kr/rest/bis/BusLocation/?ServiceKey={BUS_KEY}&route=379001000
"""

"""
정우상가 정류소에서 경유하는 모든 노선버스의 도착정보를 검색할 경우
- http://openapi.changwon.go.kr/rest/bis/BusArrives/?ServiceKey={BUS_KEY}&station=379000814

이벤트코드 EVENT_CD
(17 : 진입, 18 : 진출,
19 : 교차로통과, 33: 정주기,
없으면 null)
"""

"""
정우상가 정류소에서 10번 버스의 도착정보를 검색할 경우
- http://openapi.changwon.go.kr/rest/bis/ArriveInfo/?ServiceKey={BUS_KEY}&station=379000814&route=379000100

이벤트코드 EVENT_CD
(17 : 진입, 18 : 진출,
19 : 교차로통과, 33: 정주기,
없으면 null)
"""

"""
노선부가정보를 검색할 경우
- http://openapi.changwon.go.kr/rest/bis/BusInfo/?serviceKey={BUS_KEY}
"""

"""
전체 정류소 목록을 검색할 경우
- http://openapi.changwon.go.kr/rest/bis/Station/?ServiceKey={BUS_KEY}
"""

"""
노선부가정보를 검색할 경우
- http://openapi.changwon.go.kr/rest/bis/BusInfo/?serviceKey={BUS_KEY}
"""

"""
버스노선 목록을 검색할 경우
- http://openapi.changwon.go.kr/rest/bis/Bus/?ServiceKey={BUS_KEY}
"""


"""
경유정류소 목록을 검색할 경우
- http://openapi.changwon.go.kr/rest/bis/StationRoute/?ServiceKey={BUS_KEY}
"""

url = f'http://openapi.changwon.go.kr/rest/bis/Station/?ServiceKey={BUS_KEY}'
re = requests.get(url)
data = json.loads(re.text)

a = open("loaddata\testbus.txt",'w')
a.write(data)
a.close()