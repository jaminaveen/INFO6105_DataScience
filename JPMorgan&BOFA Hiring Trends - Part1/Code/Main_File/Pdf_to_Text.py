from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO
from PyPDF2 import PdfFileMerger, PdfFileReader
import re


class PdfConverter:
    def __init__(self, file_path):
        self.file_path = file_path

    # convert pdf file to a string which has space among words
    def convert_pdf_to_txt(self):
        rsrcmgr = PDFResourceManager()
        retstr = StringIO()
        codec = 'utf-8'
        laparams = LAParams()
        device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
        fp = open(self.file_path, 'rb')
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        password = ""
        maxpages = 0
        caching = True
        pagenos = set()
        for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password, caching=caching,
                                      check_extractable=True):
            interpreter.process_page(page)
        fp.close()
        device.close()
        str = retstr.getvalue()
        retstr.close()
        return str

    # convert pdf file text to string and save as a text_pdf.txt file

    def save_convert_pdf_to_txt(self):
        content = self.convert_pdf_to_txt()
        content = content.lower()
        content = re.sub('\.\.+', '', content)
        content = re.sub('\…\…+', '', content)
        remove_special_chars = content.translate({ord(c): '' for c in "\.{2,}!@#$%^&*()[]\\{};:,./<>?\|`~-=_+\"\“\”"})
        remove_special_chars = re.sub(r'[^a-zA-Z\s]+', '', remove_special_chars)
        remove_special_chars = remove_special_chars.replace('\n', ' ')
        remove_special_chars = ' '.join(remove_special_chars.split())
        txt_pdf = open(r'../Document_Reports/Combined_Reports.txt', 'wb')
        txt_pdf.write(remove_special_chars.encode('utf-8'))
        txt_pdf.close()
        print("=========== PDF changed to text file ===========")


def merge_pdf_file():
    merger = PdfFileMerger()
    merger.append(PdfFileReader(open(r'../Document_Reports/Report_1.pdf', 'rb')))
    merger.append(PdfFileReader(open(r'../Document_Reports/Report_2.pdf', 'rb')))
    merger.append(PdfFileReader(open(r'../Document_Reports/Report_3.pdf', 'rb')))
    merger.append(PdfFileReader(open(r'../Document_Reports/Report_4.pdf', 'rb')))
    merger.write(r'../Document_Reports/Combined_Reports.pdf')
    print('===========Merging of PDF completed ===========')


if __name__ == '__main__':
    merge_pdf_file()
    pdfConverter = PdfConverter(file_path=r'../Document_Reports/Combined_Reports.pdf')
    pdfConverter.save_convert_pdf_to_txt()
