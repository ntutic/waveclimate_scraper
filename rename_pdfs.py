import os, shutil

dir = 'scraped/'

pdfs = [pdf for pdf in os.listdir(dir) if '_news_' in pdf]
print(pdfs)

months = {
    'Jan': '1',
    'Feb': '2',
    'Mar': '3',
    'Apr': '4',
    'May': '5',
    'Jun': '6',
    'Jul': '7',
    'Aug': '8',
    'Sep': '9',
    'Oct': '10',
    'Nov': '11',
    'Dec': '12'
}

for pdf in pdfs:
    splits = pdf.split('_')
    date = splits[-2]
    date = months[date.split('-')[0]] + date[3:]
    new = 'BTB_' + splits[1] + '_' + date + '_' + splits[3]
    shutil.move(dir + pdf, dir + new)