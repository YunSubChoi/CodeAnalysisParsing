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

def flawfinderParsing(tag):
    tempText = []
    tagText = []
    for i in range(0, len(tag[0]), 1):
        tempText = (tag[0][i].text).split('./')
        tempText = tempText[1].split(':')
        del tempText[2]
        tagText.append(tempText)
    for j in range(0, len(tag[1]), 1):
        tagText[j].append(tag[1][j].text)
    for k in range(0, len(tagText), 1):
        tagText[k].append('flawfinder_result')
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
    return fileNameTag


# save date and time information to nowDate
now = datetime.datetime.now()
nowDate = now.strftime('%Y%m%d-%H%M')

# save filename to fileName
fileName = 'flawfinder-1.html'

# save filepath to filepath
currentDir = os.getcwd()
filePath = currentDir + '/' + fileName

source = ''
tagName = ['li', 'i']
tag = []
tagText = []

source = sourceRead(filePath)

source = StringIO(source)  # read as String
parsed = parse(source)  # source -> parsing as html format

# find root node
doc = parsed.getroot()

tag = findTag(tagName, doc)
tagText = flawfinderParsing(tag)
tagText = combine_duplicate_errors(tagText)

flawfinder = Element
flawfinder = to_tag(tagText, nowDate, 'flawfinder')
ElementTree(flawfinder).write(currentDir + '/flawfinder-' + nowDate + '.xml')
