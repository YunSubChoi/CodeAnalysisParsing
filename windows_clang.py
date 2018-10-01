import glob                     # 디렉토리 내 파일을 얻기 위해 사용
import os                       # 디렉토리를 바꿔야 할 경우 사용
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
    parsed = parse(source)  # source -> html형식으로 파싱

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

def clangParsing(tag):
    tempNum1 = 0
    while True:     # repeat as many as files
        tempNum2 = 0
        if tempNum1 is len(tag):
            break
        while True:
            if len(tag[tempNum1][0]) is 6:
                break
            if tempNum2 < 6:
                tempNum2 = tempNum2 + 1
            else:
                del(tag[tempNum1][0][tempNum2])
        tempNum1 = tempNum1 + 1

    tempNum1 = 0
    tempText3 = []
    tagText = []
    while True:     # repeat as many as files
        tempNum2 = 0
        tempText1 = []
        tempText2 = []
        if tempNum1 is len(tag):
            break
        tempText1 = tag[tempNum1][0][1].text    # tempText1 = file name
        tempText2.append(tempText1)

        tempText1 = (tag[tempNum1][1][0].text).split(',')
        tempText1 = tempText1[0].replace('line ', '')    # tempText1 = error location
        tempText2.append(tempText1)

        tempText1 = tag[tempNum1][0][5].text    # tempText1 = error content
        tempText2.append(tempText1)

        tagText.append(tempText2)

        tempNum1 = tempNum1 + 1
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

def clang_to_tag(tagText, nowDate):
    tagNum = 0
    clang = Element("clang")
    clang.attrib["result"] = nowDate
    while True:
        if tagNum is len(tagText):
            break
        error = Element("error")
        error.attrib["File"] = tagText[tagNum][0]
        clang.append(error)
        SubElement(error, "Location").text = "line " + tagText[tagNum][1]
        SubElement(error, "Description").text = tagText[tagNum][2]
        tagNum = tagNum + 1
    indent(clang)
    # dump(clang)
    return clang



# nowDatatime에 datetime정보 저장
now = datetime.datetime.now()
nowDatetime = now.strftime('%Y%m%d-%H_%M/')
nowDate = now.strftime('%Y%m%d-%H%M')

# folderName에 폴더명 저장
folderName = 'clangResult-' + nowDatetime

# filePath에 html파일이 있는 경로 저장
filePath = "D:/test/clangResult-20180824-17_30/"
os.chdir(filePath) # 디렉토리를 바꿔야 할 경우에만 쓰세요
fileList = []
for file in glob.glob("report-*.html"): # '*'은 모든 값을 의미
    fileList.append(filePath+file)

tagName = ['td', 'a']
tempTag = []
tag = []
tagText = []
source = []
tempSource = ''

tempNum = 0
while True:
    if tempNum is len(fileList):
        break
    tempSource = sourceRead(fileList[tempNum])
    source.append(tempSource)
    tempNum = tempNum + 1

tempNum = 0
while True:
    if tempNum is len(source):
        break
    tempTag = findTag(tagName, source[tempNum])
    tag.append(tempTag)
    tempNum = tempNum + 1

tagText = clangParsing(tag)

clang = Element
clang = clang_to_tag(tagText, nowDate)
ElementTree(clang).write('D:/test/result/clang-' + nowDate + '.xml')