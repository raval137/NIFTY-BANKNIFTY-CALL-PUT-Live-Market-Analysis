#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul 11 10:34:55 2021

@author: jaydevraval
"""

#Imports
import requests
import json
import pandas as pd
import numpy as np
import time
import os
import datetime
import csv
import re
import copy

#Intial Parameters
data = None
header = {"User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 12871.102.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.141 Safari/537.36"}
currentDate = datetime.datetime.now().strftime("%d-%m-%Y")
save_dir = os.path.join(r"/Users/jaydevraval/Documents/Stocks/stock_eod_oi_data/", "OptionChain_" + currentDate + '.xlsx')
save_dir_bhav = os.path.join(r"/Users/jaydevraval/Documents/Stocks/stock_eod_oi_data/", "BhavCopy_" + currentDate + '.xlsx')
filePath = r"/Users/jaydevraval/Documents/Stocks/stock_eod_oi_data"
stockList = []
sectorList = []
df_Stock = {}
df_BhavSector = {}
df_BhavStock = None
df = None
defaultBhavCopy = "Stock Bhav Copy"
filenameBhavCopy = []
filenameOptionChain = []
sheetNameBhavCopy = []
sheetNameOptionChain = []
df_BhavCopyBundle = {}
df_OptionChainBundle = {}

#Create Directory
def makeDir():
    global save_dir
    
    with open(save_dir , 'w') as fp:
        fp.close()
        
    with open(save_dir_bhav, 'w') as fp:
        fp.close()

#Get Data From API
def getDataFromNSE(name):
    global data
    global driver
    
    print("Getting Data for " + name)

    
    quote_url = "https://www.nseindia.com/get-quotes/derivatives?symbol=" + name
    url = "https://www.nseindia.com/api/option-chain-equities?symbol=" + name
    

    response = None
    while response is None:
        try:
            with requests.session() as s:
                s.get(quote_url, headers = header)
                time.sleep(1)
                response = s.get(url, headers = header)
        except:
            pass
     
    data = json.loads(response.text)
    if len(data) == 2:
        nsetoStockDataframe(name)

#API data to Dataframe and Saving in Local Disk  
def nsetoStockDataframe(name):
    global data
    global df_Stock
    
    # TotalCE = data['filtered']['CE']['totOI']
    # TotalPE = data['filtered']['PE']['totOI']
    records = data['records']
    currentExpiry = records['expiryDates'][0]
    
    df_Stock[name] = pd.DataFrame(columns = ["Strike Price", "CE_IV", "CE_OI", "CE_CHNGOI", "CE_PCHNGOI", "PE_IV", "PE_OI", "PE_CHNGOI", "PE_PCHNGOI"])
    for i in records['data']:
        if len(i) == 4:
            if i['expiryDate'] == currentExpiry:
                createDict = {"Strike Price" : i['strikePrice'] , "CE_IV": i['CE']['impliedVolatility'], "CE_OI": i['CE']['openInterest'] , "CE_CHNGOI" : i['CE']['changeinOpenInterest'], "CE_PCHNGOI" : i['CE']['pchangeinOpenInterest'] ,"PE_IV" : i['PE']['impliedVolatility'], "PE_OI" : i['PE']['openInterest'], "PE_CHNGOI" : i['PE']['changeinOpenInterest'], "PE_PCHNGOI" : i['CE']['pchangeinOpenInterest']}
                df_Stock[name] = df_Stock[name].append(createDict, ignore_index= True)

    # df_Stock[name].to_csv(os.path.join(save_dir, name) + ".csv", header = True)
    print("OI Dataframe Created for " + name)
    
#Pre-defined Stock List with Sectors
def getDataFromCSV():
    global stockList
    global sectorList
    global df
    df = pd.read_csv(r"/Users/jaydevraval/Documents/Stocks/Stock_Sector_FO.csv", header = 0)
    stockList = df["Stock"].tolist()
    sectorList = list(np.unique(df['Sector']))
    
#Function to write dataframes to excel
def writetoExcel():
    global df_Stock
    global stockList
    global df_BhavStock
    global df_BhavSector
     
    with pd.ExcelWriter(save_dir) as writer:
        for i in list(df_Stock.keys()):
            df_Stock[i].to_excel(writer, sheet_name = i)
    
    with pd.ExcelWriter(save_dir_bhav) as writer:
        df_BhavStock.to_excel(writer, sheet_name = "Stock Bhav Copy")
        # for i in list(df_BhavSector.keys()):
        #     df_BhavSector[i].to_excel(writer, sheet_name = i)

#Function is to retrieve BhavCopy, Process it make df_Sector available with stock with their delivery data
def getBhavCopy():
    global df_BhavSector
    global df_Stock
    global df_BhavStock
    
    #Download file from site
    try:
        CSV_URL = "https://www1.nseindia.com/products/content/sec_bhavdata_full.csv"
        
        with requests.Session() as s:
            download = s.get(CSV_URL)
        
            decoded_content = download.content.decode('utf-8')
        
            cr = csv.reader(decoded_content.splitlines(), delimiter=',')
            my_list = list(cr)
            writer = csv.writer(open("sec_bhavdata_full.csv", 'w'))
            for write in my_list:
                writer.writerow(write)
    except:
        print('Error in downloading CSV file from site')
        
    df_BhavStock = pd.read_csv("sec_bhavdata_full.csv", header = 0)
    bhavDate = df_BhavStock[' DATE1'].tolist()[0]
    
    if bhavDate == datetime.datetime.now().strftime(" %d-%-b-%Y"):
        df_BhavStock = df_BhavStock.loc[df_BhavStock['SYMBOL'].isin(stockList)]
        df_BhavStock = df_BhavStock.loc[(df_BhavStock[' SERIES'] == ' EQ')]
        df_BhavStock = df_BhavStock.drop([' SERIES', ' DATE1', ' PREV_CLOSE', ' OPEN_PRICE',  ' HIGH_PRICE', ' LOW_PRICE', ' LAST_PRICE', ' AVG_PRICE',  ' TURNOVER_LACS'], axis = 1)
        df_BhavStock = df_BhavStock.set_index('SYMBOL')
        spareList = []
        for i in df_BhavStock.index.tolist():
             spareList.append(df.set_index('Stock').loc[i]['Sector'])
        df_BhavStock['SECTOR'] = spareList
        df_BhavStock_sector = df_BhavStock.groupby("SECTOR")
        
        # for j in sectorList:
        #     df_BhavSector[j] = df_BhavStock_sector.get_group(j)

#Run Analysis Code
def runAnalysis():
    filenameBhavCopy = []
    filenameOptionChain = []
    
    

def main():
    global stockList
    
    print("Execution Started")
    makeDir()
    getDataFromCSV() #Stock_List and Sector-Wise Dataframe is available
    for i in stockList:
        getDataFromNSE(i)
    getBhavCopy()
    writetoExcel()
    # runAnalysis()
        

if __name__ == '__main__':
    #Code Sequence
    main()
    
    
    
    
    
    
    