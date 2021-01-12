import os
import re
import json
import requests
import threading
from lxml import etree
from urllib.parse import urlparse

downloadUrl = "https://www.cartoonmad.com/comic/comicpic.asp?file=/{id}/{part}/{page}"
headers = {
    "User-Agent": "Mozilla/5.0 (X11 Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
    "Referer": "https://www.cartoonmad.com/comic/"
}

qwe = 0


def chooseComic():
    global comicTitle
    global comicID
    global comicMetadata
    comicMetadata = {}

    print("输入要下载的漫画链接: ", end='')
    url = input()

    path = urlparse(url).path
    comicID = re.search(r"\b\d+\b", path).group()
    res = requests.get(url, headers=headers)
    res.encoding = 'big5'
    html = etree.HTML(res.text)
    comicTitle = html.xpath(r"//td[2]/a[@href='" + str(path) + r"']")[0].text
    parts = html.xpath(r"//table[3][@width='850']//table[@width='800']//td/a")
    pages = html.xpath(
        r"//table[3][@width='850']//table[@width='800']//td/font")
    idx = 0
    while idx < len(parts):
        part = re.search(r"\b([0-9]+)", parts[idx].text).group()
        page = re.search(r"\b([0-9]+)", pages[idx].text).group()
        comicMetadata[part] = page
        idx += 1
    pass


def choosePart():
    global targets
    targets = []

    print("请选择要下载的章节(e.g. 1-5 1): ", end='')
    wants = input().split(' ')
    for want in wants:
        if re.match(r"^\d+\-\d+$", want):
            want = list(map(int, want.split('-')))
            want[1] += 1
            for i in range(want[0], want[1]):
                if i >= len(comicMetadata):
                    raise Exception("无效的章节数: " + str(i))
                targets.append(i)
        elif re.match(r"^\d+$", want):
            want = int(want)
            if want >= len(comicMetadata):
                raise Exception("无效的章节数: " + str(want))
            targets.append(int(want))
        else:
            pass
    targets = list(set(targets))


def getPage(part: str) -> int:
    return int(comicMetadata[part])


def buildNum(num: str) -> str:
    num = list(num)
    length = len(num)
    if length < 3:
        num.insert(0, str(0))
        num = buildNum(num="".join(num))
    num = "".join(num)
    return num


def buildDownloadUrl(id: str, part: str, page: str) -> str:
    return downloadUrl.replace("{id}", id).replace("{part}", part).replace("{page}", page)


def buildDownloadList():
    global downloadList
    global errorList
    downloadList = {}

    for target in targets:
        target = buildNum(str(target))
        partTotalPage = getPage(target) + 1
        downloadList[target] = {}
        for i in range(1, partTotalPage):
            downloadList[target][buildNum(str(i))] = buildDownloadUrl(
                comicID,
                target,
                buildNum(str(i))
            )

    errorList = downloadList


def download(url: str, title: str, part: str, page: str):
    try:
        ext = re.search(r"(?!.*\/).*", url).group()
        if not os.path.exists("./downloads/" + title + "/" + "第" + str(part) + "话/"):
            os.makedirs("./downloads/" + title + "/" + "第" + str(part) + "话/")
        req = requests.get(url, headers=headers)
        fo = open("./downloads/" + title + "/" + "第" +
                  str(part) + "话/" + ext + ".jpg", "wb")
        fo.write(req.content)
        fo.close()
        del errorList[part][page]
    except Exception:
        pass
    finally:
        if not os.path.exists("./logs/"):
            os.mkdir("./logs")
        write("./logs/" + comicID +".json", json.dumps(errorList))


def createADownloadThread(data: dict):
    for part in data:
        for page in data[part]:
            download(data[part][page], comicTitle, part, page)


def downloadStart(threadNum: int):
    buildDownloadList()
    chunks = []
    i = 0
    while i < threadNum:
        chunks.append({})
        i += 1

    i = 0
    for part in downloadList:
        for page in downloadList[part]:
            if i >= threadNum:
                i = 0
            if part not in chunks[i]:
                chunks[i][part] = {}
            chunks[i][part][page] = downloadList[part][page]
            i += 1

    threads = []
    for chunk in chunks:
        threads.append(threading.Thread(
            target=createADownloadThread,
            args=(chunk,)
        ))
    print("Downloading...")
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()


def write(path: str, content: str):
    fo = open(path, "w")
    fo.write(content)
    fo.close()


def read(path: str) -> str:
    fo = open(path, "r")
    content = fo.read()
    fo.close()
    return content


def main():
    chooseComic()
    choosePart()
    downloadStart(128)
    print("Finished :)")


main()
