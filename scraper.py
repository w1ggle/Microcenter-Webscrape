# https://www.microcenter.com/robots.txt states that this should be fine to scrape their website. If a rep from microcenter wants me to remove it, feel free to contact me and I will remove this. Same goes with cpu passmark!

#TODO plans to add full catalog once I can figure out webdriver to switch between pages


import setup
from bs4 import BeautifulSoup
import requests
import csv
import re
from selenium import webdriver
driver = webdriver.Chrome()
driver.get('https://www.cpubenchmark.net/CPU_mega_page.html')
html = driver.page_source
PassSoup = BeautifulSoup(html)

#desirable 2-in-1 laptops from NJ microcenter
URL = "https://www.microcenter.com/search/search_results.aspx?N=4294967288+4294818548+4294819270+4294819837+4294814254+4294814572+4294805366+4294814062+4294816439+4294818783&NTK=all&sortby=pricelow&rpp=96&storeID=075"

print("Installing packages") #get packages #TODO make setup an if statement
#setup.install()
print("Done installing packages")


print("Scraping URL") #get html from website #TODO add if statement to check if we got a request, else print error
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/99.0", 
    "method": "GET"
}
page_to_scrape = requests.get(URL,headers=headers) 
MicroSoup = BeautifulSoup(page_to_scrape.text, 'html.parser') 
#page_to_scrape = requests.get("https://www.cpubenchmark.net/CPU_mega_page.html",headers=headers)
#PassSoup = BeautifulSoup(page_to_scrape.text, 'html.parser') 

print("Response received from microcenter")

roles = PassSoup.findAll('tr', attrs={"role":"row"})
print(roles)
print("Tabulating data") #parse data into table
file = open('output.csv', 'w')
writer = csv.writer(file)
writer.writerow(['Brand', 'Model', 'CPU', 'Ram (GB)', 'Ram Type', 'Storage (GB)', 'GPU', 'Price ($)', 'Refurbed' , 'Open Box', 'Color', 'Size' ])


products = MicroSoup.findAll('div', attrs={"class":"result_right"}) #TODO look into using regex
for product in products: #getting specs

    brand = product.find("a").get("data-brand") 
    model = product.find("a").get("data-name").replace('&quot','"') 

    index = model.rfind('-')
    color = model[index+2:]

    if (model.find("Refurbished") == -1):
        refurbishedStatus = ""
    else:
        refurbishedStatus = "x"

    index = model.find(";")
    if(index == -1):
        index = model.find("-in-1")
    model = model[:index]

    index = model.rindex(" ")+1
    size = model[index:-1]
    model = model[:index]

    fullDetails = product.find("div", attrs={"class":"h2"}).text.split("; ") 
    for detail in fullDetails[1:]:
        if(detail.find("Processor") != -1):
            cpu = detail[:-17]
            if(cpu.find("AMD") != -1):
                cpu = cpu[5:]
            else:
                index = cpu.rindex("i")
                cpu = cpu[index:]
                cpu = re.sub(" ..th Gen ","-",cpu)
        elif(detail.find("RAM") != -1):
            ram = detail[1:-4]
            index = ram.find("GB")
            ramCapacity = ram[:index]
            ramType = ram[index+3:]
        elif(detail.find("Solid State Drive") != -1):
            storage = detail[:-18].replace("TB","000")
            storage = storage.replace("GB","")
        elif(detail.find("AMD") != -1 or detail.find("Intel") != -1 or detail.find("NVIDIA") != -1 ):
            gpu = detail
        else:
            gpu = None




    
    priceOpenBox = product.find("div", attrs={"class":"clearance"}) #going to open box #TODO check if faster going to price wrapper first then check in there
    priceOpenBoxIndex = priceOpenBox.text.find("$") #checking if open box exists
    
    if (priceOpenBoxIndex == -1):
        price = (product.find("span", attrs={"itemprop":"price"}).text) #normal price
        openBoxStatus = ""
    else:
        price = (priceOpenBox.text[priceOpenBoxIndex:]) #open box
        openBoxStatus = "x"

    price = float(price.replace(',', '').replace('$', ''))

    writer.writerow([brand, model, cpu, ramCapacity, ramType, storage, gpu, price,refurbishedStatus, openBoxStatus, color, size]) #TODO mark if refurbed, get laptop size, get cpupassmark scores, see if its possible to get ALL inventory and not just 96 results, add my own personal score/rating, make csv 2 sheets where 1 is for calulations and other is for front end

file.close() 
print("DONE! Check output.csv")