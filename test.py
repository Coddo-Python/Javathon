date_time_start = datetime.datetime(2022, 3, 26, 21, 00, 00)
date_time_end = datetime.datetime(2022, 3, 27, 9, 00, 00)
start = int((time.mktime(date_time_start.timetuple())))
end = int((time.mktime(date_time_end.timetuple())))
# response = json.dumps(r.text)
url_base = 'URL'
url_path = '/PATH'
token = 'MY_TOKEN'
query_params = {
    'nextBatchToken': nextBatchToken,
    'end': end,
    'size': '5',
    'start': start,
    'riskLevels': 'critical'
}
headers = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json;charset=utf-8'}
response = requests.get(url_base + url_path, params=query_params, headers=headers)
# archive = response.text
decodedResponse = json.loads(response.text)
# decodedResponse = json.dumps(response.json())
r = decodedResponse['data']
count = r['totalCount']
json.dump(response.json(), archive)
for i in r:
    nextBatchToken = r['nextBatchToken']
    if 'nextBatchToken' in r:
        print('nextBatchToken')  # I add the variable here, oculting
        nextBatchToken = r['nextBatchToken']
    else:
        print('cabo')
