import os                       # for directory path
import datetime                 # to get date and time
from lxml.html import parse     # parsing as html format
from io import StringIO         # string input/output module
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
    with open(filePath, mode="r") as f:
        while True:
            line = f.readline()
            if line is '':
                break
            else:
                source = source + line
    return source

def findTag(tagName, doc):
    tag = []
    tempTag = []

    # doc.findall(".//tagname")
    for i in range(0, len(tagName), 1):
        tempTag = doc.findall('.//' + tagName[i])
        tag.append(tempTag)
    return tag

def ratsMakeTagList(tag, allTag):
    tempList = []
    for i in range(0, len(allTag), 1):
        if allTag[i]=='message' or allTag[i]=='name' or allTag[i]=='line':
            tempList.append(allTag[i])
    allTag = tempList

    tempTag1 = []
    tempTag2 = []
    messageNum = 0
    nameNum = 0
    lineNum = 0
    for j in range(0, len(allTag), 1):
        if allTag[j]=='message':
            message = tag[0][messageNum].text
            messageNum = messageNum + 1
        if allTag[j]=='name':
            tempTag1.append(tag[1][nameNum].text)
            nameNum = nameNum + 1
        if allTag[j]=='line':
            tempTag1.append(tag[2][lineNum].text)
            lineNum = lineNum + 1
            if j<len(allTag)-1 and allTag[j+1]!='line':
                tempTag1.append(message)
                tempTag2.append(tempTag1)
                tempTag1 = []
    tempTag1.append(message)
    tempTag2.append(tempTag1)

    return tempTag2

def combine_duplicate_errors(tagText):
    duplicate_tagNum = []
    for i in range(0, len(tagText)-1, 1):
        for j in range(i+1, len(tagText), 1):
            if tagText[i][0]==tagText[j][0]:
                tagText[i][1] = tagText[i][1] + ';;;' + tagText[j][1]
                tagText[i][2] = tagText[i][2] + ';;;' + tagText[j][2]
                duplicate_tagNum.append(j)
    tagTextLen = len(tagText)
    for m in range(tagTextLen, 0, -1):
        if m in duplicate_tagNum:
            del tagText[m]
    return tagText

def ratsParsing(tag):
    tagText = []
    for i in range(0, len(tag), 1):
        tempTag = []
        filename = tag[i][0].split('/')
        tempTag.append(filename[len(filename)-1])   # filename[len(filename)-1] is real filename
        if len(tag[i]) > 3:     # if errorline > 1
            lineString = ''
            for j in range(1, len(tag[i])-1, 1):
                lineString = lineString + tag[i][j] + ';'
        else:       # if errorline = 1
            lineString = tag[i][1] + ';'
        tempTag.append(lineString)
        tempTag.append((tag[i][len(tag[i])-1]).replace('\n', ''))      # tag[i][len(tag[i])-1 is error text
        tagText.append(tempTag)
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


# save date and time information to nowDate
now = datetime.datetime.now()
nowDate = now.strftime('%Y%m%d-%H%M')

# save filename to fileName
fileName = 'rats1-0.txt'
# save current directory path to currentDir
currentDir = os.getcwd()
# save filepath to filePath
filePath = currentDir + '/' + fileName

source = ''
tagName = ['message', 'name', 'line']
tag = []
tagText = []
allTag = []
tempTag = []

source = sourceRead(filePath)

source = StringIO(source)  # read as String
parsed = parse(source)  # source -> parsing as html format

# find root node
doc = parsed.getroot()

for child in doc.iter():
    allTag.append(child.tag)

tag = findTag(tagName, doc)
tag = ratsMakeTagList(tag, allTag)
tagText = ratsParsing(tag)
tagText = combine_duplicate_errors(tagText)

rats = Element
rats = to_tag(tagText, nowDate, 'rats')
ElementTree(rats).write(currentDir + '/rats-' + nowDate + '.xml')