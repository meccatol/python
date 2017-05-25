#!/user/bin/python
# -*- coding: utf-8 -*-
# zemyblue 2016.5.24

import sys
import os
import subprocess

if len(sys.argv) == 1:
    print __file__ + " -o [dSYM path] -f [filePath] -arch [arch]"
    exit(1)


# 입력되는 arguments를 parsing 한다.
argvs = sys.argv[1:]
parsingArgv = {"-arch":"arm64"}
index = 0
while index < len(argvs):
    if argvs[index] == "-o":
        dSYMargv = argvs[index + 1]
        parsingArgv["-o"] = argvs[index + 1]
        index += 1
    elif argvs[index] == "-f":
        inputfilepath = argvs[index + 1]
        parsingArgv["-f"] = argvs[index + 1]
        index += 1
    elif argvs[index] == "-arch":
        archParam = argvs[index + 1]
        parsingArgv["-arch"] = argvs[index + 1]
        index += 1

    index += 1



# dSYM의 실제 경로를 구한다.
if parsingArgv["-o"]:
    path = dSYMargv + "/Contents/Resources/DWARF/"
    filenames = os.listdir(path)
    for filename in filenames:
        fullPath = os.path.join(path, filename)
        dSYMPath = fullPath



# atos를 통해서 입력되는 주소를 심볼릭한다.
def symbolicateAddress(addresslist):
    commend = "atos -arch %s -o %s -l %s" % (parsingArgv["-arch"], dSYMPath, " ".join(addresslist))
    # print "commend :", commend
    commendResult = subprocess.Popen(commend, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for readline in commendResult.stdout.readlines():
        if readline[:4] == "atos":
            continue
        return readline.strip()

    return ""


# 정수인지 확인
def isNumber(num):
    try:
        judge = str(float(num))
        return False if(judge=='nan' or judge=='inf' or judge =='-inf') else True
    except ValueError:
        return False



# 파일을 로드한다.
symbolfile = open(parsingArgv["-f"])

BandBaseAddr = "";
while True:
    line = symbolfile.readline()
    if not line: break
    # print line.strip()
    lineWords = line.split()
    # print lineWords

    if len(lineWords) > 3 and isNumber(lineWords[0]) and lineWords[1].lower() == "band":
        if BandBaseAddr == "":
            # binary image의 baseAddress는 "0x00000001001f9fa8 Band + 18431122"의 hex 전제 주소(2)에서 상대위치값인 18431122(4)를 빼도록 한다.
            BaseAddr = int(lineWords[2], 0) - int(lineWords[5])
            BandBaseAddr = "0x%x" % BaseAddr

        # 심볼릭한다.
        callbackSymbol = symbolicateAddress([BandBaseAddr, lineWords[2]])
        print "%2d  %s\t\t\t\t%s %s" % (int(lineWords[0]), lineWords[1], lineWords[2], callbackSymbol)
        continue
    else:
        print line.strip()

symbolfile.close()
