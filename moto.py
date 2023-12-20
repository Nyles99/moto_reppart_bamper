import json
from turtle import pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import requests
from bs4 import BeautifulSoup
import os
import shutil
import csv
from PIL import Image, UnidentifiedImageError
import time



headers = {
    "Accept" : "application/json, text/javascript, */*; q=0.01",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
}

input_model = "foto_moto"
#input_number = "Введи один, если не уверен в себе и хочешь обновить марки и модели в списке - "

# Адрес сайта, с которого мы будем получать данные
url_byn = "https://www.google.com/search?q=курс+доллара+к+белорусскому+рублю"
    
# Получаем содержимое страницы
response = requests.get(url_byn)
    
# Создаем объект BeautifulSoup для парсинга HTML-разметки
soup = BeautifulSoup(response.content, 'html.parser')
    
# Получаем элемент с курсом валюты
result = soup.find("div", class_="BNeawe iBp4i AP7Wnd").get_text()
    
# Возвращаем курс валюты как число
usd_byn =  float(result.replace(",", ".")[:4])
print("На сегодня 1USD = "+ str(usd_byn) + "BYN")

folder_name = input_model + "_fotku_" + time.strftime('%Y-%m-%d')
if os.path.exists(folder_name):
    print("Папка уже есть")
else:
    os.mkdir(folder_name)

watermark = Image.open("moe.png")
with open(f"{input_model}_data_bamper.csv", "w", encoding="utf-8") as file_data:
    writer = csv.writer(file_data)

    writer.writerow(
        (
            "АРТИКУЛ",
            "МАРКА",
            "МОДЕЛЬ",
            "ГОД",
            "ССЫЛКА НА ЗАПЧАСТЬ",
            "ТОПЛИВО",
            "ОБЪЕМ",
            "ТИП ДВИГАТЕЛЯ",
            "КОРОБКА",
            "ТИП КУЗОВА",
            "ЗАПЧАСТЬ",
            "ОПИСАНИЕ",
            "ПОД ЗАКАЗ",
            "ЦЕНА",
            "НОВАЯ",
            "ФОТО",
        )
    )
n = 1

for year_in in range(2000, 2024):
    for i in range(1,7):
        url = f"https://bamper.by/zchbu/moto/god_{year_in}-{year_in}/price-ot_70/store_Y/isused_Y/?ACTION=REWRITED3&FORM_DATA=moto%2Fgod_{year_in}-{year_in}%2Fprice-ot_70%2Fstore_Y%2Fisused_Y&more=Y&PAGEN_1=" + str(i)
        print(url)
        req = requests.get(url, headers=headers)
        src = req.text
        soup = BeautifulSoup(src, "lxml")
        href_part = soup.find_all("div", class_="add-image")
        #print(href_part)

        moto = {}
        for item in href_part:
            
            item = str(item)
            item = item[item.find("href")+6 : item.find("target=") -2 ]
            #print(item)
            href_to_zapchast = "https://bamper.by/" + str(item)
            moto[n] = href_to_zapchast
            print(n, href_to_zapchast)
            n += 1
            #print(href_to_zapchast)
        
    for number, href_to_zapchast in moto.items():
        req = requests.get(url=href_to_zapchast, headers=headers)
        src = req.text

        soup = BeautifulSoup(src, "lxml")

        #print(item)
        number_href_reverse = href_to_zapchast[::-1]
        number_href_reverse_second = number_href_reverse[1:]
        number_href_reverse = number_href_reverse_second[: number_href_reverse_second.find("/")]
        name_href = number_href_reverse[::-1]
        #print(name_href)
            
        price_obj = soup.find_all("meta", itemprop="price")
        #print (price_obj)
        if price_obj != []:
            for item_price in price_obj:
                price = item_price.get("content").replace(" ","")
                price = round(float(price)/usd_byn)
        else:
            price = "Цена не указана"
        print(price)
        

        marka_obj = soup.find_all("span", itemprop="name")
        for item_marka in marka_obj:
            all_title_name = str(item_marka)
            string = all_title_name[all_title_name.find("<b>") + 1 : ]
            number_b = string.find('</b>')
            name_part = string[2:number_b]
            model_and_year = string[number_b+8 :]
            marka = model_and_year[: model_and_year.find(" ")]
            model = model_and_year[model_and_year.find(" ")+1 : model_and_year.find(",")]
            year = model_and_year[model_and_year.find(",")+2 : model_and_year.find("г.")]

        artical_obj = soup.find_all("span", class_="data-type f13")
        for item_artical in artical_obj:
            artical = item_artical.text

            
        print(marka, model, year, price, number)

                
        order = None
        status = "Б/у"
        info = None
        info_obj = soup.find_all("span", class_="media-heading cut-h-375")
        for item_info in info_obj:
            info = item_info.text.replace("  ","").replace("\n","")
            info_lower = info.lower()
            if "ПОД ЗАКАЗ" in info:
                order = "ПОД ЗАКАЗ"
            # print(info)
            if "новый" in info_lower:
                status = "Новая"
            elif "новая" in info_lower:
                status = "Новая"
            elif "новые" in info_lower:
                status = "Новые"
        print(status, order, info)
        foto = None
            
        image_obj = str(soup.find("img", class_="fotorama__img"))
        # print(image_obj)
        foto = "https://bamper.by" + image_obj[image_obj.find("src=")+5 : image_obj.find("style=")-2]
        #print(foto)
        if foto != "https://bamper.by/local/templates/bsclassified/images/nophoto_car.png":
            img = requests.get(foto)
            img_option = open(f"{folder_name}/{name_href}.png", 'wb')
            img_option.write(img.content)
            #img_option.close

            im = requests.get(foto)

            with open(f"{folder_name}/{name_href}.png", "wb+") as file:
                file.write(im.content)  # Для сохранения на компьютер
            try:
                im = Image.open(f"{folder_name}/{name_href}.png")
                pixels = im.load()  # список с пикселями
                x, y = im.size  # ширина (x) и высота (y) изображения
                min_line_white = []
                n=0
                for j in range(y):
                    white_pix = 0

                    for m in range(x):
                        # проверка чисто белых пикселей, для оттенков нужно использовать диапазоны
                        if pixels[m, j] == (248,248,248):         # pixels[i, j][q] > 240  # для оттенков
                            white_pix += 1
                    if white_pix == x:
                        n += 1
                    #print(white_pix, x, n)

                    #print(white_pix)
                    min_line_white.append(white_pix)
                left_border = int(min(min_line_white)/2)
                #print(left_border)
                im.crop(((left_border+15), n/2+20, (x-left_border-20), y-(n/2)-20)).save(f"{folder_name}/{name_href}.png", quality=95)





                img = Image.open(f"{folder_name}/{name_href}.png")
                print(foto)
                #img = Image.open(f"fotku/{name_href}.png")    
                img.paste(watermark,(-272,-97), watermark)
                img.paste(watermark,(-230,1), watermark)
                img.save(f"{folder_name}/{name_href}.png", format="png")
                img_option.close
                #os.remove("img.png")
                #print(f"{name_href} - неверный формат или ерунда")
            except UnidentifiedImageError:
                foto = "Битая фотка"
                print("Битая фотка")
                os.remove(f"{folder_name}/{name_href}.png")
        else:
            foto = "Нет фотографии"
            print(name_href , "без фотки")
                
        benzik_obj = soup.find_all("div", style="font-size: 17px;")
        fuel = None
        transmission = " "
        engine = " "
        volume = None
        car_body = None
        # print(benzik_obj)
        for item_benzik in benzik_obj:
            benzik = None
            benzik = item_benzik.text.replace("  ","").replace("\n","")
            if "л," in benzik:
                volume = benzik[benzik.find("л,") - 5 : benzik.find("л,") + 1]
            if "бензин" in benzik:
                fuel = "бензин"
            elif "дизель" in benzik:
                fuel = "дизель"
            elif "электро" in benzik:
                fuel = "электро"
            elif "гибрид" in benzik:
                fuel = "гибрид"
            if "TSI" in benzik:
                engine = "TSI"
            elif "TDI" in benzik:
                engine = "TDI"
            elif "MPI" in benzik:
                engine = "MPI"
            elif "CRDI" in benzik:
                engine = "CRDI"
            if "АКПП" in benzik:
                transmission = "АКПП"
            elif "МКПП" in benzik:
                transmission = "МКПП"
            elif "вариатор" in benzik:
                transmission = "вариатор"
            if "седан" in benzik:
                car_body = "седан"
            elif "хетчбек" in benzik:
                car_body = "хетчбек"
            elif "внедорожник" in benzik:
                car_body = "внедорожник"
            elif "универсал" in benzik:
                car_body = "универсал"
            elif "кабриолет" in benzik:
                car_body = "кабриолет"
            elif "микроавтобус" in benzik:
                car_body = "микроавтобус"
            elif "пикап" in benzik:
                car_body = "пикап" 
        #print(volume, fuel, transmission, engine, car_body)
        #print(benzik)

        file = open(f"{input_model}_data_bamper.csv", "a", encoding="utf-8", newline='')
        writer = csv.writer(file)

        writer.writerow(
            (
                artical,
                marka,
                model,
                year,
                href_to_zapchast,
                fuel,
                volume,
                engine,
                transmission,
                car_body,
                name_part,
                info,
                order,
                price,
                status,
                foto
            )
        )
        file.close()


input(f"Парсинг по {input_model} законичил свою работу, нажми Enter")



