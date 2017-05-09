import base64
str = """aHR0cHM6Ly93d3cuc2hhYmFrLmdvdi5pbC9jeWJlcnRlY2hub2xvZ3kvUGFnZXMvMDExMTAwMTEtMDExMDEwMDAtMDExMDAwMDEtMDExMDAwMTAtMDExMDAwMDEtMDExMDEwMTE=tLmFzcHg"""
str = """MTAxMDAxMTAxMTAxMDAwMDExMDAwMDEwMTEwMDAxMDAxMTAwMDAxMDExMDEwMTEuY29t"""
print base64.b64decode(str)
#https://www.shabak.gov.il/cybertechnology/Pages/01110011-01101000-01100001-01100010-01100001-01101011

str2 = "01110011-01101000-01100001-01100010-01100001-01101011"
print([chr(int(i, 2)) for i in str2.split("-")])
#['s', 'h', 'a', 'b', 'a', 'k']

#shabak ip - 147.237.1.239