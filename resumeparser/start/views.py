import os
import zipfile
import re
import PyPDF2
import camelot
from django.shortcuts import render

from pdfrw import PdfReader

from start.forms import UploadFileForm
from start.models import UserResumes

try:
    from xml.etree.cElementTree import XML
except ImportError:
    from xml.etree.ElementTree import XML

WORD_NAMESPACE = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
PARA = WORD_NAMESPACE + 'p'
TEXT = WORD_NAMESPACE + 't'

relevtags = ['Hobbies', 'HOBBIES', 'ExtraCurricularActivities', 'Activites', 'ACTIVITIES', 'Projects', 'PROJECTS',
             'WORK', 'Work', 'ACHIEVEMENTS', 'Achievements', 'SKILLS', 'Skills', 'Experience', 'EXPERIENCE',
             'Qualification', 'QUALIFICATION', 'Education', 'EDUCATION', 'EDUCATIONAL', 'Educational']


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
    # print("hiiii")
    pdfobj = open("UploadedResumes/" + str(name), 'rb')
    pdfreader = PyPDF2.PdfFileReader(pdfobj)
    # print(pdfreader.numPages)
    x = name[0:len(name) - 3]
    desturl = str(x) + "txt"
    fob = open("UploadedResumes/" + desturl, "w", encoding="utf-8")
    for page in pdfreader.pages:
        s = page.extractText()
        # print(s)
        lines = s.split("\n")
        # print(lines)
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
        text = get_docx_text("UploadedResumes/" + str(name))
        text = os.linesep.join([s for s in text.splitlines() if s])
        s = str(name)
        fo = open('UploadedResumes/' + s[:s.rfind('.')] + ".txt", "w", encoding="utf-8")
        fo.write(text)
        fo.close()


def index(request):
    if request.method == "POST":
        uploadform = UploadFileForm(request.POST, request.FILES)
        if uploadform.is_valid():
            # print("its in normal")
            # saving the file
            file = request.FILES['file']

            pdf_file = UserResumes(pdf=file)
            pdf_file.save()

            print(file.name)
            print(file.content_type)

            f = os.path.join('resumeparser', 'UploadedResumes', file.name)
            # print(text)
            # print(s)
            # num = re.sub(r'[\n][\n]', "", text)

            pdfobj = open(f, 'rb')
            pdfreader = PyPDF2.PdfFileReader(pdfobj)
            pages = pdfreader.numPages
            tables = extractnotables(f)
            title = extracttitle(f)

            user = UserResumes(title=title, tables=tables, pages=pages, pdf=file)
            # user = UserResumes(tables=tables, pinfo=pinfo, cgpa=cgpa, mobile=mobno, email=email, objective=obj,
            #                   education=edu, skill=skill, achievements=achieve, projects=projects, hobbies=hobb)
            user.save()
            return render(request, 'success.html',
                          {'fileform': UploadFileForm(),
                           'files': UserResumes.objects.all()})
    else:
        print("default form created")
        form = UploadFileForm()
        # book = UserResumes(name="ujjwal", address="vfdv", mobile="9760017250", email="uj00007@gmail.com")
        # book.save()
        return render(request, 'success.html',
                      {'fileform': form,
                       'files': UserResumes.objects.all()})


def extractnotables(resume):
    tables = camelot.read_pdf(resume)
    notables = tables.n

    return notables


def extracttitle(file):
    # Extract pdf title from pdf file
    title = PdfReader(file).Info.Title
    # Remove surrounding brackets that some pdf titles have
    if title:
        title = title.strip('()')
    else:
        title = ""
    return title


def extractmobile(s):
    m = re.search('[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]', s)
    if m:
        # print("hello")
        found = m.group(0)
        return found


def extractcgpa(s):
    m = re.findall('[0-9][.][0-9]', s)
    if m:
        # print("hello")
        found = m
        return found[0]


def extractemail(s):
    # print("vsdf")
    m = re.findall('[ ][a-z|0-9]+[@][a-z]+[.][a-z]+[ ]', s)
    if m:
        # print("hello")
        found = m
        return found[0]


def extractperc(s):
    m = re.findall('[0-9][0-9][.][0-9][0-9]', s)
    if m:
        # print("hello")
        found = m
        return found


def extractpersonalinfo(s):
    text = ""
    for i in s:
        i = str(i).strip()
        # print(i)
        if i != "CAREER" and i != "Objective" and i != "Career" and i != "OBJECTIVE":
            text = text + str(i) + " "
        else:
            # print("gaya")
            break
    return text
    # print(ne_chunk(pos_tag(text.strip().split('.'))))


def extractobjective(s):
    global relevtags
    text = ""
    for i in range(0, len(s)):
        temp = str(s[i]).strip()
        # print(i)

        if not temp.find("OBJECTIVE"):
            # print(temp)
            # print("found")
            for j in range(i + 1, len(s)):
                if str(s[j]).strip() not in relevtags:
                    text = text + str(s[j]).strip() + " "
                else:
                    break
        else:

            continue
    return text
    # print(ne_chunk(pos_tag(text.strip().split('.'))))


def extracteducation(s):
    global relevtags
    text = ""
    for i in range(0, len(s)):
        temp = str(s[i]).strip()
        # print(i)

        if not temp.find("EDUCATION") or not temp.find("EDUCATIONAL") or not temp.find("Education") or not temp.find(
                "Educational") or not temp.find("QUALIFICATION"):
            # print(temp)
            # print("found")
            for j in range(i + 1, len(s)):
                if str(s[j]).strip() not in relevtags:
                    text = text + str(s[j]).strip() + " "
                else:
                    break
        else:

            continue
    return text


def extractskills(s):
    global relevtags
    text = ""
    for i in range(0, len(s)):
        temp = str(s[i]).strip()
        # print(i)

        if not temp.find("SKILLS") or not temp.find("Skills"):
            # print(temp)
            # print("found")
            for j in range(i + 1, len(s)):
                if str(s[j]).strip() not in relevtags:
                    text = text + str(s[j]).strip() + " "
                else:
                    break
        else:

            continue
    return text


def extractachievements(s):
    global relevtags
    text = ""
    for i in range(0, len(s)):
        temp = str(s[i]).strip()
        # print(i)

        if not temp.find("Achievements") or not temp.find("ACHIEVEMENTS"):
            # print(temp)
            # print("found")
            for j in range(i + 1, len(s)):
                if str(s[j]).strip() not in relevtags:
                    text = text + str(s[j]).strip() + " "
                else:
                    break
        else:

            continue
    return text


def extractprojects(s):
    global relevtags
    text = ""
    for i in range(0, len(s)):
        temp = str(s[i]).strip()
        # print(i)

        if not temp.find("Projects") or not temp.find("PROJECTS"):
            # print(temp)
            # print("found")
            for j in range(i + 1, len(s)):
                if str(s[j]).strip() not in relevtags:
                    text = text + str(s[j]).strip() + " "
                else:
                    break
        else:

            continue
    return text


def extracthobbies(s):
    global relevtags
    text = ""
    for i in range(0, len(s)):
        temp = str(s[i]).strip()
        # print(i)

        if not temp.find("Activities") or not temp.find("ACTIVITIES"):
            # print(temp)
            # print("found")
            for j in range(i + 1, len(s)):
                if str(s[j]).strip() not in relevtags:
                    text = text + str(s[j]).strip() + " "
                else:
                    break
        else:

            continue
    return text
