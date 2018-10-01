import datetime                 # date와 time을 얻기 위해 사용
from lxml.html import parse     # html양식으로 파싱
from io import StringIO         # 문자열 입출력 모듈
from xml.etree.ElementTree import Element, SubElement, dump, ElementTree

def sourceRead(filePath):
    source = ''
    # web문서를 source(text문서)로 가져오기
    with open(filePath, mode="r") as f:
        while True:
            line = f.readline()
            if line is '':
                break
            else:
                source = source + line
    return source

def findTag(tagName, source):
    tag = []
    tempTag = []
    tempNum = 0
    # html 문서로 파싱(변환)
    source = StringIO(source)  # 문자열로 읽음
    parsed = parse(source)      # source -> html형식으로 파싱

    # root node 찾기
    doc = parsed.getroot()

    # doc.findall(".//태그")    # 찾고자 하는 태그명
    while True:
        if tempNum is len(tagName):
            break
        tempTag = doc.findall('.//'+tagName[tempNum])
        tag.append(tempTag)
        tempNum = tempNum + 1
    return tag

def flawfinderParsing(tag):
    tempNum1 = 0
    tempNum2 = 0
    tempText = []
    tagText = []
    while True:
        if tempNum1 is len(tag[0]):
            break
        tempText = (tag[0][tempNum1].text).split('./')
        tempText = tempText[1].split(':')
        del tempText[2]
        tagText.append(tempText)
        tempNum1 = tempNum1 + 1
    while True:
        if tempNum2 is len(tag[1]):
            break
        tagText[tempNum2].append(tag[1][tempNum2].text)
        tempNum2 = tempNum2 + 1
    return tagText

def indent(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

def flawfinderResult_to_tag(tagText, nowDate):
    tagNum = 0
    flawfinder = Element("flawfinder")
    flawfinder.attrib["result"] = nowDate
    while True:
        error = Element("error")
        error.attrib["File"] = tagText[tagNum][0]
        flawfinder.append(error)
        SubElement(error, "Location").text = "line " + tagText[tagNum][1]
        SubElement(error, "Description").text = tagText[tagNum][2]
        tagNum = tagNum + 1
        if tagNum is len(tagText):
            break
    indent(flawfinder)
    # dump(flawfinder)
    return flawfinder



# nowDate에 datetime정보 저장
now = datetime.datetime.now()
nowDate = now.strftime('%Y%m%d-%H%M')

# fileName에 파일명 저장
fileName = 'flawfinder.html'

# filePath에 html파일이 있는 경로 저장
filePath = '/var/lib/jenkins/workspace/testCWE/' + fileName

source = ''
tagName = ['li', 'i']
tag = []
tagText = []

source = sourceRead(filePath)
tag = findTag(tagName, source)
tagText = flawfinderParsing(tag)

flawfinder = Element
flawfinder = flawfinderResult_to_tag(tagText, nowDate)
ElementTree(flawfinder).write('/var/lib/jenkins/workspace/testCWE/flawfinder-' + nowDate + '.xml')
