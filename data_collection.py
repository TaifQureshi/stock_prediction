import bs4 as bs
import pickle
import requests
import datetime as dt
import os
import pandas as pd
import pandas_datareader.data as web
import quandl as qdl
from quandl.errors.quandl_error import NotFoundError
from matplotlib import pyplot as plt
from matplotlib import style
import numpy as np

style.use('ggplot')


#get 500 companies name
def save_sp500_tickers():
  res = requests.get('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
  soup = bs.BeautifulSoup(res.text, "lxml")
  table = soup.find('table', {'class': 'wikitable sortable'})
  tickers = []
  for row in table.findAll('tr')[1:]:
    ticker = row.findAll('td')[0].text
    tickers.append(ticker)
    
  with open("sp500.pickle", "wb") as f:
    pickle.dump(tickers, f)
  
  return tickers



# get data 
def get_data_from_quandl(reload_sp500 = False):
    if reload_sp500:
        tickers = save_sp500_tickers()
    else:
        with open ("sp500.pickle",'rb') as f:
            tickers = pickle.load(f)
    if not os.path.exists('stock_dfs'):
        os.makedirs('stock_dfs')
        
    start = dt.datetime(2000,1,1)
    end = dt.datetime(2018,11,25)
    
    for ticker in tickers:
        print(ticker)
        try:
            if not os.path.exists('stock_dfs/{}.cvs'.format(ticker)):
                df = qdl.get("WIKI/"+ticker, start_date = start, end_date = end,use_retries = False)
                df.to_csv('stock_dfs/{}.csv'.format(ticker))
            else:
                print('Already have {}'.format(ticker))
        except NotFoundError as e:
            print('error in : {} '.format(ticker))
        except:
          pass


# complie data
def compile_data():
  with open ("sp500.pickle",'rb') as f:
    tickers = pickle.load(f)
    
  main_df = pd.DataFrame()
  
  for count, ticker in enumerate(tickers):
    try:
      df = pd.read_csv('stock_dfs/{}.csv'.format(ticker))
      df.set_index('Date', inplace=True)

      df.rename(columns = {'Adj. Close':ticker}, inplace=True)
      df.drop(['Ex-Dividend', 'Split Ratio', 'Adj. Open', 'Adj. High', 'Adj. Low','Adj. Volume', 'Open', 'High', 'Low', 'Close', 'Volume'], 1 , inplace=True)
  #     print(df.head())
      if main_df.empty:
        main_df = df

      else:
        main_df = main_df.join(df,how='outer')


      if count % 10 == 0:
        print(count)
    except:
        pass  
  print(main_df.head())
  
  main_df.to_csv('sp500_joint_close.csv')
  


# data visulization
def visualize_data():
  df = pd.read_csv('sp500_joint_close.csv')
  df_corr = df.corr()
  print(df_corr.head())
  data = df_corr.values
  fig = plt.figure()
  ax = fig.add_subplot(1,1,1)
  heatmap = ax.pcolor(data, cmap=plt.cm.RdYlGn)
  fig.colorbar(heatmap)
  ax.set_xticks(np.arange(data.shape[0]) + 0.5, minor=False)
  ax.set_yticks(np.arange(data.shape[1]) + 0.5, minor=False)
  ax.invert_yaxis()
  ax.xaxis.tick_top()
  
  colum_lables = df_corr.columns
  row_lables = df_corr.index
  
  ax.set_xticklabels(colum_lables)
  ax.set_yticklabels(row_lables)
  plt.xticks(rotation=90)
  heatmap.set_clim(-1,1)
  plt.tight_layout()
  plt.show()