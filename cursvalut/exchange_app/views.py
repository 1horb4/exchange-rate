from django.shortcuts import render
from bs4 import BeautifulSoup
import requests
import os
import json
from dotenv import load_dotenv
from time import time

# Create your views here.
time_update = 3600


def pars_curs(url, tag):
    load_dotenv()
    headers = {
        'Accept': os.environ.get('ACCEPT'),
        'User-Agent': os.environ.get('USER-AGENT')
    }

    response = requests.get(url, headers=headers)
    src = response.text
    soup = BeautifulSoup(src, 'lxml')
    curs_cbr = soup.find(*tag)
    return curs_cbr.text[:5].replace(',', '.')


def exchange(request):
    now = int(time())
    try:
        file_stat = os.stat('curs_valut.json')
    except FileNotFoundError:
        file_stat = False

    if file_stat is False or int((now - file_stat.st_mtime) / time_update) >= 1:
        total_dict = {'Рубли': 1,
                      'USD ЦБ': pars_curs('https://www.banki.ru/products/currency/usd/?location=moskva',
                                          ('div', {"class": "Text__sc-j452t5-0 bCCQWi", 'data-test': 'text'})),
                      'USD покупки ВТБ': pars_curs('https://www.sravni.ru/bank/vtb/valjuty/',
                                                   ('td', {'title': "Курс", })),
                      'USD AliExpress': pars_curs('https://helpix.ru/currency/',
                                                  ('span', {'class': "b-currency", }))}
        with open('curs_valut.json', 'w') as file:
            json.dump(total_dict, file)

    with open('curs_valut.json', 'r') as file:
        total_dict = json.load(file)

    if request.method == 'GET':
        context = {
            'currencies': total_dict,
        }
        return render(request, 'exchange_app/index.html', context=context)

    if request.method == 'POST':
        if request.POST.get('from-amount'):
            from_amount = float(request.POST.get('from-amount'))
        else:
            from_amount = 1
        from_curr = request.POST.get('from-curr')
        to_curr = request.POST.get('to-curr')

        converted_amount = round((float(total_dict[to_curr]) / float(total_dict[from_curr])) * from_amount, 3)

        context = {
            'currencies': total_dict,
            'from_curr': from_curr,
            'to_curr': to_curr,
            'from_amount': from_amount,
            'converted_amount': converted_amount,
        }

        return render(request, 'exchange_app/index.html', context=context)
