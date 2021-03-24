import time
import numpy as np
import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup as BS

def render_page(url):
    driver = webdriver.Safari()
    driver.get(url)
    time.sleep(3)
    r = driver.page_source
    driver.quit()
    return r
  
def scraper(start_date, end_date):
    base_url = 'https://www.wunderground.com/history/daily/us/ny/new-york-city/date/{}'
    fdata = []
    for date in pd.date_range(start_date, end_date):

        url = base_url.format(str(date.date()))
        
        try:
            r = render_page(url)
        
            soup = BS(r, "html.parser")
            container = soup.find('lib-city-history-observation')
            check = container.find('tbody')

            df = []
            for c in check.find_all('tr', class_='ng-star-inserted'):
                for i in c.find_all('td', class_='ng-star-inserted'):
                    trial = i.text
                    trial = trial.strip('  ')
                    df.append(trial)

            s = int(len(df) / 10)

            data = pd.DataFrame(np.array(df).reshape(s,10))
            data['date'] = date
            fdata.append(data)
            
        except:
            print("Error: {}".format(date))
            pass
        
    return fdata
  
def main():
    df = scraper('2016-01-01','2016-01-07')
    # -- concat dataframes
    data = pd.concat(df)
    
    # -- Clean the data
    data[1] = data[1].map(lambda x: int(x.replace('\xa0F',''))) 
    data[2] = data[2].map(lambda x: int(x.replace('\xa0F','')))
    data[3] = data[3].map(lambda x: int(x.replace('\xa0%','')))
    data[5] = data[5].map(lambda x: int(x.replace('\xa0mph','')))
    data[6] = data[6].map(lambda x: int(x.replace('\xa0mph','')))
    data[7] = data[7].map(lambda x: float(x.replace('\xa0in',''))) 
    data[8] = data[8].map(lambda x: float(x.replace('\xa0in','')))
    
    cols = ['Time','TemperatureF', 'DewPointF','Humidity','WindDir','WindSpeed','Gust','Pressure','Precipitation','Condition','Date']
    data.columns = cols

    data['datetime'] = pd.to_datetime(data['Date'].astype(str) + ' ' + data['Time'])
    
    # Write to file
    data.to_csv('weather.csv', index=False)
