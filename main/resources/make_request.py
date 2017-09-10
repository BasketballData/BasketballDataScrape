import requests

r = requests.get('http://www.fiba.basketball/ls/#13229&13554-A-2')

print(r.text)