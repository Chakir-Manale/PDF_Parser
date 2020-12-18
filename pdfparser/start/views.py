import os
import zipfile
import re
import PyPDF2
import camelot
from django.shortcuts import render

from pdfrw import PdfReader

from start.forms import UploadFileForm
from start.models import UserPDF

try:
    from xml.etree.cElementTree import XML
except ImportError:
    from xml.etree.ElementTree import XML

WORD_NAMESPACE = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
PARA = WORD_NAMESPACE + 'p'
TEXT = WORD_NAMESPACE + 't'


def convertpdf(name):
    # print("test")
    pdfobj = open("UploadedPDFs/" + str(name), 'rb')
    pdfreader = PyPDF2.PdfFileReader(pdfobj)
    # print(pdfreader.numPages)
    x = name[0:len(name) - 3]
    desturl = str(x) + "txt"
    fob = open("UploadedPDFs/" + desturl, "w", encoding="utf-8")
    for page in pdfreader.pages:
        s = page.extractText()
        # print(s)
        lines = s.split("\n")
        # print(lines)
        for line in lines:
            fob.write((line + "\n"))

    fob.close()
    pdfobj.close()


def index(request):
    if request.method == "POST":
        uploadform = UploadFileForm(request.POST, request.FILES)
        if uploadform.is_valid():
            # saving the file
            file = request.FILES['file']

            pdf_file = UserPDF(pdf=file)
            pdf_file.save()

            print(file.name)
            print(file.content_type)

            f = os.path.join('pdfparser', 'UploadedPDFs', file.name)

            pdfobj = open(f, 'rb')
            pdfreader = PyPDF2.PdfFileReader(pdfobj)
            pages = pdfreader.numPages
            tables = extractnotables(f)
            title = extracttitle(f)

            user = UserPDF(title=title, tables=tables, pages=pages, pdf=file)

            user.save()
            return render(request, 'index.html',
                          {'fileform': UploadFileForm(),
                           'files': UserPDF.objects.all()})
    else:
        print("default form created")
        form = UploadFileForm()
        return render(request, 'index.html',
                      {'fileform': form,
                       'files': UserPDF.objects.all()})


# nombre de table
def extractnotables(resume):
    tables = camelot.read_pdf(resume)
    notables = tables.n

    return notables


# pdf title
def extracttitle(file):
    # Extract pdf title from pdf file
    title = PdfReader(file).Info.Title
    # Remove surrounding brackets that some pdf titles have
    if title:
        title = title.strip('()')
    else:
        title = ""
    return title
