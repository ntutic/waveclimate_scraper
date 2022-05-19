import PyPDF2
import re
import os
import pandas as pd
import datetime
from colorama import Style, Fore

class ParsePDF:
    def __init__(self, path_pdf):
        self.path = path_pdf
        self.df = pd.DataFrame([], columns=['street_nb', 'street', 'city', 'province', 'date_filing', 'type'])
        


    def find_text(self, pdfs, keywords, search=''):

        # Iterate over PDFs
        for pdf in pdfs:
            pdf_obj = open(self.path + pdf, 'rb')
            pdf_reader = PyPDF2.PdfFileReader(pdf_obj)

            # Get all text of PDF in a paragraph
            text = ''
            for page in range(pdf_reader.numPages):
                page_obj = pdf_reader.getPage(page)

                text_raw = page_obj.extractText()
                text += text_raw.replace('\n', '') + ' '

            # Clean up text
            # //todo change all multi-space to single

            # Get text following keyword or continue if not found
            for keyword in keywords:
                while True:
                    if keyword in text.lower():
                        if search not in text:
                            break

                        found = text.lower().find(search)
                        text_sub = text[found + len(search):].strip() 



                        # Find numbers //todo non-numeric address start
                        pattern_nb = re.compile('^(\d+)')
                        re_nb = pattern_nb.match(text_sub)
                        if re_nb:
                            street_nb = text_sub[re_nb.span()[0]:re_nb.span()[1]]
                            text_sub = text_sub[re_nb.span()[1]:].strip() 
                        else:
                            continue
                    
                        # Find street name
                        street = text_sub.split(' in ')[0]
                        city = text_sub.split(' in ')[1].split(',')[0]
                        province = text_sub.split(' in ')[1].split(',')[1].strip().split(' ')[0].strip(',.')


                        print(f' \
                            {Fore.WHITE}{text[:found]}\
                            {Fore.GREEN}{text[found : found + len(search)]}\
                            {Fore.RED}{text[found + len(search) : len(street + city + province + 3)]}\
                        ')
                        
                        print(street_nb, street, city, province)

                        os.system(pdf)

                        while True:
                            go = input('Continue (y/n/m)? : ')
                            if go == 'y':
                                add = True
                                break
                            elif go == 'n':
                                add = False
                                break
                            elif go == 'm':
                                street_nb = input('Street number : ')
                                street = input('Street name : ')
                                city = input('City : ')
                                province = input('Province : ')
                                add = True
                                break

                        
                        if add:
                            self.df = self.df.append({
                                'street_nb': street_nb,
                                'street': street,
                                'city': city,
                                'province': province,
                                'date_filing': pdf.split('_')[2],
                                'type': keyword

                            }, ignore_index=True)
                        

                    else:
                        break



if __name__ == '__main__':
    
    path_pdf = 'scraped/'

    PP = ParsePDF(path_pdf=path_pdf)

    # Get list of PDFs to scrape
    pdf_names = [pdf for pdf in os.listdir(PP.path) if '_news_' in pdf]
    dic = {}
    for pdf_name in pdf_names:
        date = datetime.datetime.strptime(pdf_name[9:].split('.')[0], '%m-%d-%Y_%H-%M-%S')
        dic[date] = pdf_name
    keys = sorted(dic.keys())
    pdfs = []
    for key in keys:
        pdfs.append(dic[key])

    # Scrape list
    PP.find_text(pdfs=pdfs, keywords=['acqui', 'dispo'], search='located at')