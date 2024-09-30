import requests

url = 'http://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getMinuDustFrcstDspth'
params ={'serviceKey' : '0ugQ4AGF76S72YECTC1qiZKWP6XZALIW%2BUPlkc0wnolNxDyY6S2rU7%2F0HKK5KqHh4k%2Br6FfRWtWAdG%2B7%2BFEDdg%3D%3D', 'returnType' : 'xml', 'numOfRows' : '100', 'pageNo' : '1', 'searchDate' : '2020-11-14', 'InformCode' : 'PM10' }

response = requests.get(url, params=params)
print(response.content)