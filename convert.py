import glob
import fitz
import os


def convertPDF(img_path, pdf_path, pdf_name):
    doc = fitz.open()
    for img in sorted(glob.glob(img_path + "*.jpg")):
        imgDoc = fitz.open(img)
        pdfbytes = imgDoc.convertToPDF()
        imgPDF = fitz.open("pdf", pdfbytes)
        doc.insertPDF(imgPDF)
    doc.save(pdf_path + pdf_name)
    doc.close()


def buildNum(num: str) -> str:
    num = list(num)
    length = len(num)
    if length < 3:
        num.insert(0, str(0))
        num = buildNum(num="".join(num))
    num = "".join(num)
    return num


part = 0

while part < 137:
    name = buildNum(str(part))
    convertPDF(
        r"./downloads/進擊的巨人/第" + name+"话/",
        r"./downloads/進擊的巨人/PDF/",
        r"第" + name + "话.pdf"
    )

    part += 1