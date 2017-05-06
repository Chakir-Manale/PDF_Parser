import os
import zipfile

import PyPDF2
from django.shortcuts import render

from start.forms import UploadFileForm
from start.models import UserResumes

try:
    from xml.etree.cElementTree import XML
except ImportError:
    from xml.etree.ElementTree import XML

WORD_NAMESPACE = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
PARA = WORD_NAMESPACE + 'p'
TEXT = WORD_NAMESPACE + 't'



def get_docx_text(path):
    """
    Take the path of a docx file as argument, return the text in unicode.
    """
    document = zipfile.ZipFile(path)
    xml_content = document.read('word/document.xml')
    document.close()
    tree = XML(xml_content)

    paragraphs = []
    for paragraph in tree.getiterator(PARA):
        texts = [node.text
                 for node in paragraph.getiterator(TEXT)
                 if node.text]
        if texts:
            paragraphs.append(''.join(texts))

    return '\n\n'.join(paragraphs)


def convertpdf(name):
    print("hiiii")
    pdfobj=open("UploadedResumes/"+str(name), 'rb')
    pdfreader=PyPDF2.PdfFileReader(pdfobj)
    #print(pdfreader.numPages)
    x = name[0:len(name)-3]
    desturl =str(x)+"txt"
    fob = open("UploadedResumes/"+desturl, "w", encoding="utf-8")
    for page in pdfreader.pages:
        s = page.extractText()
        print(s)
        lines=s.split("\n")
        print(lines)
        for line in lines:
            fob.write((line + "\n"))

    fob.close()
    pdfobj.close()


def handle_uploaded_file(file, name, content):
    fo = open("UploadedResumes/" + str(name), "wb+")
    for chunk in file.chunks():
        fo.write(chunk)
    fo.close()
    if content.endswith("pdf"):
        convertpdf(name)
    if content.endswith("document"):

        text = get_docx_text("UploadedResumes/"+str(name))
        text = os.linesep.join([s for s in text.splitlines() if s])
        s=str(name)
        fo = open('UploadedResumes/'+s[:s.rfind('.')]+".txt", "w",encoding="utf-8")
        fo.write(text)
        fo.close()


def index(request):
    if request.method=="POST":
        uploadform=UploadFileForm(request.POST, request.FILES)
        if uploadform.is_valid():
            print("its in normal")
            file = request.FILES['file']
            print(file.name)
            print(file.content_type)
            handle_uploaded_file(file, file.name, file.content_type)
            form = UploadFileForm()
            #addfile(request.session['name'], file.name)
            return render(request, 'success.html', {})
    else:
        print("default form created")
        form=UploadFileForm()
        #book = UserResumes(name="ujjwal", address="vfdv", mobile="9760017250", email="uj00007@gmail.com")
        #book.save()
    return render(request,'index.html',{'fileform':form})