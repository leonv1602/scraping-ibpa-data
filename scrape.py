import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import os
import openpyxl
import matplotlib.pyplot as plt
import re
import urllib.request
from weasyprint import HTML

# Define the URL of the website
url = "https://www.phei.co.id/Data/HPW-dan-Imbal-Hasil"

response = requests.get(url)
html_response = response.content
text_find = response.text
df_list = pd.read_html(html_response)

start_ = re.search('<div id="dnn_ctr1477_GovernmentBondBenchmark_idIGSYC_tdTgl">', text_find).start()
date_yc = text_find[start_ :100+start_]
date_yc = date_yc.split(' ')[-2]
split = date_yc.find('<')
clean_date = date_yc[:split]
clean_date

if int(clean_date.split('-')[0]) < 10:
    cleaner_date = clean_date.split('-')
    cleaner_date[0] = '0' + cleaner_date[0]
    clean_date = '-'.join(cleaner_date)
clean_date

dict_month_number = {"Januari": "01", 
                     "Februari": "02", 
                     "Maret": "03", 
                     "April": "04", 
                     "Mei": "05", 
                     "Juni": "06", 
                     "Juli": "07", 
                     "Agustus": "08", 
                     "September": "09", 
                     "Oktober": "10", 
                     "November": "11", 
                     "Desember": "12",}

sub_path =  f'Scrape PHEI/{clean_date.split("-")[2]}-{dict_month_number.get(clean_date.split("-")[1])}-{clean_date.split("-")[1]}'

try:
    os.makedirs(sub_path)
    print(f"Folder {sub_path} created!")
except FileExistsError:
    print(f"Folder {sub_path} already exists")

sub_path_image = sub_path+'/image'
try:
    os.makedirs(sub_path_image)
    print(f"Folder {sub_path_image} created!")
except FileExistsError:
    print(f"Folder {sub_path_image} already exists")

sub_path_py_image = sub_path+'/py-image'
try:
    os.makedirs(sub_path_py_image)
    print(f"Folder {sub_path_py_image} created!")
except FileExistsError:
    print(f"Folder {sub_path_py_image} already exists")

sub_path_pdf = sub_path+'/pdf'
try:
    os.makedirs(sub_path_pdf)
    print(f"Folder {sub_path_pdf} created!")
except FileExistsError:
    print(f"Folder {sub_path_pdf} already exists")

# Save as PDF
HTML(url).write_pdf(f'Scrape PHEI/{clean_date.split("-")[2]}-{dict_month_number.get(clean_date.split("-")[1])}-{clean_date.split("-")[1]}/pdf/{clean_date}.pdf')

# Save image from Website
img_location_url = text_find[re.search('ChartPic', text_find).start():re.search('ChartPic', text_find).start()+200].split(' ')[0][:-1]
imgURL = "https://www.phei.co.id/"+img_location_url
urllib.request.urlretrieve(imgURL,f'Scrape PHEI/{clean_date.split("-")[2]}-{dict_month_number.get(clean_date.split("-")[1])}-{clean_date.split("-")[1]}/image/{clean_date}.jpeg')

def prepare_data(df, type_df):
    copy_df = df.copy()
    copy_df.drop(columns = copy_df.columns[[0, -1]], inplace = True)
    copy_df['type'] = type_df
    return copy_df

sbn_data = prepare_data(df_list[2], 'sbn')
sbsn_data = prepare_data(df_list[3], 'sbsn')
retail_data= prepare_data(df_list[4], 'retail')

bond_data = pd.concat((sbn_data, 
                             sbsn_data,
                             retail_data), axis = 0).reset_index(drop = True)

bond_data.iloc[:,1] /= 100
bond_data.iloc[:,2:-1] /= 10000
bond_data.to_excel(f'Scrape PHEI/{clean_date.split("-")[2]}-{dict_month_number.get(clean_date.split("-")[1])}-{clean_date.split("-")[1]}/Bond-Data-{clean_date}.xlsx', 
            sheet_name=clean_date)

df = pd.concat((df_list[0],df_list[1]), axis = 0)[['Tenor Year', 'Today']]
df['Tenor Year'] /= 10
df['Today'] /= 1e6
df.rename(columns = {'Today': 'IBPA Yield'}, inplace = True)
df.set_index('Tenor Year', inplace=True)

def spot_rate(df):
    spot_data = df.values.copy()
    for j in range(2,df.shape[0]):
        minus = 0
        for k in range(1,j):
            minus -= spot_data[j]/(1+spot_data[k])**k
        spot_data[j] = ((1+df.iloc[j])/(1+minus))**(1/j)-1
    return spot_data

df['Spot-Rate'] = spot_rate(df)

plt.plot(df.index, df['IBPA Yield'], label = 'Yield Curve')
plt.plot(df.index, df['Spot-Rate'], label = 'Spot Rate')
plt.legend()
plt.title(f'YCB and ZCB IDR {clean_date}')
plt.grid()
plt.savefig(f'Scrape PHEI/{clean_date.split("-")[2]}-{dict_month_number.get(clean_date.split("-")[1])}-{clean_date.split("-")[1]}/py-image/{clean_date}.jpeg')

df.to_excel(f'Scrape PHEI/{clean_date.split("-")[2]}-{dict_month_number.get(clean_date.split("-")[1])}-{clean_date.split("-")[1]}/Yield-Curve-{clean_date}.xlsx', 
            sheet_name=clean_date)
