from selenium import webdriver
from selenium.common.exceptions import ElementNotVisibleException, ElementNotSelectableException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.chrome.service import Service

import models
from app import db
from models import Temp_Anomaly, C02_Concentration, Sea_Level_Rise
import csv
import time
import os

def data_collections(URL, FilePath):

    # Set file path for downloads
    options = webdriver.ChromeOptions()
    prefs = {"download.default_directory": "C:\\Uni\\CSC2033\\Climate Datasets\\"}
    options.add_experimental_option("prefs", prefs)

    # Initialise Web Driver
    service = Service("C:/Users/ethan/OneDrive - Newcastle University/Desktop/chromedriver.exe")
    driver = webdriver.Chrome(service=service,options=options)

    # Open URL
    driver.get(URL)

    driver.maximize_window()
    time.sleep(3)

    # Agree to terms and conditions
    driver.find_element(By.XPATH, "/html/body/div[5]/div/div/div/div/div[2]/button").click()

    # Create wait case to allow webpage to catchup
    wait = WebDriverWait(driver,20, 3, ignored_exceptions=[ElementNotVisibleException, ElementNotSelectableException, TimeoutException])

    # Click on First Download Button
    driver.find_element(By.XPATH, "/html/body/main/div/div[3]/div/div[3]/div[2]/nav/ul/li[4]").click()

    # Click on Download Button
    wait.until(expected_conditions.element_to_be_clickable((By.XPATH,"/html/body/main/div/div[3]/div/div[4]/div/div[2]/div/button"))).click()

    # Allow time for download to complete before closing browser
    time.sleep(3)
    driver.close()

    # Rename File
    old_name = r"C:/Uni/CSC2033/Climate Datasets/climate-change.csv"
    new_name = FilePath

    os.rename(old_name, new_name)

def Load_Data(file_name):
    # Read csv file and load data to array
    f = open(file_name, 'r')
    reader = csv.reader(f)
    next(reader)
    data = []
    for r in reader:
        data.append(r)
    f.close
    return data  # Return array of climate change data

def write_to_database(FilePath_List):

    try:
        for p in range(0, len(FilePath_List)):
            file_name = FilePath_List[p]
            data = Load_Data(file_name)

            for i in data:
                if p == 0:
                    record = Temp_Anomaly(**{
                        'Entity' : i[0],
                        'Code' : i[1],
                        'Day' : i[2],
                        'Temperature_Anomaly' : i[3]
                    })
                    db.session.add(record)  # Add all records
                elif p == 1:
                    record = Sea_Level_Rise(**{
                        'entity': i[0],
                        'code': i[1],
                        'day': i[2],
                        'sea_level_rise_average': i[3],
                    })
                    db.session.add(record)  # Add all records
                elif p == 2:
                    record = C02_Concentration(**{
                        'entity': i[0],
                        'code': i[1],
                        'day': i[2],
                        'average_co2_concentrations': i[3],
                        'trend_co2_concentrations': i[4]
                    })
                    db.session.add(record)  # Add all records

        db.session.commit()  # Commit records
        print("Success: Data written to database")
    except:
        db.session.rollback()  # Rollback changes on error
        print("Rollback: Failed to write to database")
    finally:
        db.session.close()

def delete_datasets(FilePath_List):

    for d in range(0,len(FilePath_List)):
        # Check to see if file exists
        if os.path.exists(FilePath_List[d]):
            # delete file
            os.remove(FilePath_List[d])
        else:
            print("File does not exist")

def clear_databases():

    # Clear all data from climate change tables
    models.Temp_Anomaly.query.delete()
    models.Sea_Level_Rise.query.delete()
    models.C02_Concentration.query.delete()

def update_datasets():

    URL_List = [
        "https://ourworldindata.org/explorers/climate-change?facet=none&country=~OWID_WRL&Metric=Temperature+anomaly&Long-run+series%3F=false",
        "https://ourworldindata.org/explorers/climate-change?facet=none&country=~OWID_WRL&Metric=Sea+level+rise&Long-run+series%3F=false",
        "https://ourworldindata.org/explorers/climate-change?facet=none&country=~OWID_WRL&Metric=CO%E2%82%82+concentrations&Long-run+series%3F=false"]

    FilePath_List = [r"C:/Uni/CSC2033/Climate Datasets/temperature-change.csv",
                     r"C:/Uni/CSC2033/Climate Datasets/sea-level-rise.csv",
                     r"C:/Uni/CSC2033/Climate Datasets/co2-concentration.csv"]

    # Clear previous version of datasets
    delete_datasets(FilePath_List)

    for i in range(0, len(URL_List)):
        try:
            data_collections(URL_List[i], FilePath_List[i])
        except:
            print("Unable to update Datasets")
            break

    # Clear database before updating it
    clear_databases()

    # Write new datasets to database
    write_to_database(FilePath_List)
