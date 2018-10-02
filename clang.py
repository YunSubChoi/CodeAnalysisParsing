import os                       # for directory path
import glob                     # 디렉토리 내 파일을 얻기 위해 사용
import datetime                 # date와 time을 얻기 위해 사용
from lxml.html import parse     # html양식으로 파싱
from io import StringIO         # 문자열 입출력 모듈
from xml.etree.ElementTree import Element, SubElement, dump, ElementTree

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
    # html 문서로 파싱(변환)
    source = StringIO(source)  # 문자열로 읽음
    parsed = parse(source)  # source -> html형식으로 파싱

    # root node 찾기
    doc = parsed.getroot()

    # doc.findall(".//태그")    # 찾고자 하는 태그명
    for i in range(0, len(tagName), 1):
        tempTag = doc.findall('.//' + tagName[i])
        tag.append(tempTag)
    return tag

def clangParsing(tag):
    for i in range(0, len(tag), 1):     # repeat as many as files
        tempNum = 0
        while True:
            if len(tag[i][0]) is 6:
                break
            if tempNum < 6:
                tempNum = tempNum + 1
            else:
                del(tag[i][0][tempNum])

    tempText3 = []
    tagText = []
    for j in range(0, len(tag), 1):     # repeat as many as files
        tempText1 = []
        tempText2 = []

        tempText1 = tag[j][0][1].text    # tempText1 = file name
        tempText2.append(tempText1)

        tempText1 = (tag[j][1][0].text).split(',')
        tempText1 = tempText1[0].replace('line ', '')    # tempText1 = error location
        tempText2.append(tempText1)

        tempText1 = tag[j][0][5].text    # tempText1 = error content
        tempText2.append(tempText1)

        tagText.append(tempText2)

    for k in range(0, len(tagText), 1):
        tagText[k].append('clang_result')
    return tagText

def to_tag(tagText, nowDate, fileName):
    fileNameTag = Element(fileName)
    fileNameTag.attrib["result"] = nowDate
    for tagNum in range(0, len(tagText), 1):
        error = Element("error")
        error.attrib["File"] = tagText[tagNum][0]
        fileNameTag.append(error)
        SubElement(error, "Location").text = "line " + tagText[tagNum][1]
        SubElement(error, "Description").text = tagText[tagNum][2]
    indent(fileNameTag)
    dump(fileNameTag)
    return fileNameTag



# nowDatatime에 datetime정보 저장
now = datetime.datetime.now()
nowDatetime = now.strftime('%Y%m%d-%H_%M/')
nowDate = now.strftime('%Y%m%d-%H%M')

# folderName에 폴더명 저장
folderName = 'clangResult-' + nowDatetime
currentDir = os.getcwd()
filePath = currentDir + '/' + folderName
# filePath에 html파일이 있는 경로 저장

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

for i in range(0, len(fileList), 1):
    tempSource = sourceRead(fileList[i])
    source.append(tempSource)

for j in range(0, len(source), 1):
    tempTag = findTag(tagName, source[j])
    tag.append(tempTag)

tagText = clangParsing(tag)

clang = Element
clang = to_tag(tagText, nowDate, 'clang')
ElementTree(clang).write(currentDir + '/clang-' + nowDate + '.xml')