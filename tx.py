## PYTHON
#https://code.visualstudio.com/docs/python/python-tutorial

## COM
#https://pbpython.com/windows-com.html
#http://timgolden.me.uk/pywin32-docs/html/com/win32com/HTML/QuickStartClientCom.html

## Package
# https://captainbin.tistory.com/entry/%ED%8C%8C%EC%9D%B4%EC%8D%AC-%EB%B0%B0%ED%8F%AC-%ED%8C%8C%EC%9D%BC-%EB%A7%8C%EB%93%A4%EA%B8%B0

## Remote
#https://stackoverflow.com/questions/47653013/python-get-a-size-of-a-network-path-folder

import os

print('hello')

pwd = r'\\localhost\abcde'
os.listdir(r'\\localhost\abcde')

for f in os.listdir(r'\\localhost\abcde'):
    sf = os.path.join(r'\\localhost\abcde', f)
    print(f, sf)
    print(os.path.getsize(sf))

d = [os.path.getsize(f) for f in os.listdir(pwd) if os.path.isfile(f)]
print(d)
