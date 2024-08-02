import requests
import json

"""
Base : 창원버스정보시스템
URL : https://bus.changwon.go.kr/
"""

"""
100번 일반형버스의 위치정보를 검색할 경우
- http://openapi.changwon.go.kr/rest/bis/BusLocation/?ServiceKey=인증키&route=379001000
"""

"""
정우상가 정류소에서 경유하는 모든 노선버스의 도착정보를 검색할 경우
- http://openapi.changwon.go.kr/rest/bis/BusArrives/?ServiceKey=인증키&station=379000814
"""

"""
정우상가 정류소에서 10번 버스의 도착정보를 검색할 경우
- http://openapi.changwon.go.kr/rest/bis/ArriveInfo/?ServiceKey=인증키&station=379000814&route=379000100
"""

"""
노선부가정보를 검색할 경우
- http://openapi.changwon.go.kr/rest/bis/BusInfo/?serviceKey=인증키
"""

"""
전체 정류소 목록을 검색할 경우
- http://openapi.changwon.go.kr/rest/bis/Station/?ServiceKey=인증키
"""

"""
노선부가정보를 검색할 경우
- http://openapi.changwon.go.kr/rest/bis/BusInfo/?serviceKey=인증키
"""

"""
버스노선 목록을 검색할 경우
- http://openapi.changwon.go.kr/rest/bis/Bus/?ServiceKey=인증키
"""


"""
경유정류소 목록을 검색할 경우
- http://openapi.changwon.go.kr/rest/bis/StationRoute/?ServiceKey=인증키
"""

async def station(BUS_KEY, station):
    """이벤트코드 EVENT_CD
(17 : 진입, 18 : 진출,
19 : 교차로통과, 33: 정주기,
없으면 null)"""
    ex = '12421'
    url = f'http://openapi.changwon.go.kr/rest/bis/BusLocation/?ServiceKey={BUS_KEY}&route=379030060'
    res = requests.get(url)
    json(res)
    print('test')