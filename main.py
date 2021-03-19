# -*- coding: utf-8 -*-
from nltk.corpus import stopwords
from bs4 import BeautifulSoup
import requests
import kivy
import re
import pickle
from kivy.app import App
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.bubble import Bubble
from kivy.uix.gridlayout import GridLayout
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.uix.pagelayout import PageLayout
from kivy.lang import Builder
from kivy.core.clipboard import Clipboard, CutBuffer
import webbrowser
import time

Window.keyboard_anim_args = {'d': 2, 't': 'in_out_expo'}
Window.softinput_mode = "below_target"

Builder.load_string("""
#:import Clipboard kivy.core.clipboard.Clipboard

<PageLayout>:
    name:"pagelayout"
    border: '20dp'
    
    BoxLayout: 
        orientation: 'vertical'      
        
        Button:
        	text:"Amazon'a Git"
        	on_release: app.amazon()
        	size_hint: (1,.1)
        	
        AsyncImage: 
            source: 'rsz_amazonnn.png'
        
        Button: 
            text: 'Yapıştır'
            size_hint: (1,.15)
            on_release: root.ids.address.text = app.passte()
             
        TextInput:
            id: address
            hint_text: 'Ürün Adresini Yazınız...'
            size_hint: (1,.1)
            multiline: False
            on_text: app.process()
            
        Button: 
            text: 'Analiz'
            size_hint: (1,.15)
            on_release: app.Tahmin()
        Button:
            text: 'Temizle'
            size_hint: (1,.1)
            on_release: app.Temizle()
        
    BoxLayout: 
        canvas: 
            Color: 
                rgba: 255 / 255., 161 / 255., 2 / 255., 1
            Rectangle: 
                pos: self.pos 
                size: self.size
        
        orientation: 'vertical'
            
        Label: 
            text: "Yapay Zeka ile Amazon Ürün Analizi v.0.1"
	""")
kivy.require('1.9.0')
    
class MultipleLayout(PageLayout):
    pass

class ÜrünAnaliziApp(App):
    def build(self):
        return MultipleLayout()
    
    def _ensure_clipboard(self):
    	global Clipboard, CutBuffer
    	if not Clipboard:
    		from kivy.core.clipboard import Clipboard, CutBuffer
           
    def passte(self):
    	self._ensure_clipboard
    	data = Clipboard.paste()
    	return data
    		
    def amazon(self):
    	webbrowser.open('https://www.amazon.com.tr/')
    
    def process(self): 
        urun = self.root.ids.address.text 
        return urun
    
    def Temizle(self):
        self.root.ids.address.text  = ''
        
    def Model(self, veri):
        c = pickle.load(open("count_vect", 'rb'))
        loaded = pickle.load(open("mNB_Kivy", 'rb'))
        yorumlar_vektor = c.transform(veri)
        predx = loaded.predict(yorumlar_vektor)
        y_pred = [1 if i > 0.5 else 0 for i in predx]

        olumlu = (int(y_pred.count(1))/len(y_pred))*100
        return olumlu

    def Veri(self, adres):
        url_yeni = ""
        url = adres
        sayac = 0
        for i in url:
            url_yeni += i
            if i == "/":
                sayac += 1
            if sayac == 6:
                break
            
        url_yeni = url.replace("dp/","product-reviews/")
        url = url_yeni + "ref=cm_cr_arp_d_paging_btm_next_1?ie=UTF8&reviewerType=all_reviews""&pageNumber="
        
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"}
        liste = []
        liste_uzunlugu = []
        sayfa = 1
        sonraki_sayfa = ""
        while True:
            sonraki_sayfa = url + str(sayfa)
            req = requests.get(sonraki_sayfa, headers=headers)
            soup = BeautifulSoup(req.content,"html.parser")
            texts = soup.find_all("span", attrs={"data-hook" : "review-body"})
            for i in range(len(texts)):
                liste.append(str([texts[i].find('span').text.strip()]))
                #print(texts[i].find('span').text.strip())
            time.sleep(0.5)
            
            if len(liste_uzunlugu) > 0 and liste_uzunlugu.count(liste_uzunlugu[len(liste_uzunlugu)-1]) > 1:
                break
            
            sayfa += 1
            liste_uzunlugu.append(len(liste))

        yorumlar_temiz = []
        etkisizler = list(stopwords.words('Turkish'))
        for text in liste:
            x = str(text)
            x = text.lower()
            x = re.sub(r'\<a href', ' ', x)
            x = re.sub(r'&amp;', '', x)
            x = re.sub(r'<br />', ' ', x)
            x = re.sub(r"^\s+|\s+$", "", x)
            x = re.sub(r'[_"\-;%()|+&=*%.,!?:#$@\[\]/]', ' ', x)
            x = re.sub(r'\'', ' ', x)
            x = re.sub('\s{2,}', ' ', x)
            x = re.sub(r'\s+[a-zA-Z]\s+', ' ', x)
            x = re.sub(r'\^[a-zA-Z]\s+', ' ', x)
            x = re.sub(r'\s+', ' ', x, flags=re.I)
            x = re.sub(r'^b\s+', '', x)
            x = re.sub(r'\W', ' ', str(x))
            x = x.split()
            x = [word for word in x if word not in etkisizler]
            x = ' '.join(x)
            yorumlar_temiz.append(x)
        return yorumlar_temiz
        
    def Tahmin(self):
        self.url = self.process()
        layout = GridLayout(cols = 1, padding = 0)
        layout.text_size: (10,100)
        kapat = Button(text='Tamam', size_hint=(1,.1))

        if self.url.strip() == "":
            popupLabel = Label(text = "Lütfen Ürün Adresini Yazınız!")
            layout.add_widget(popupLabel)
            layout.add_widget(kapat)
            
            pop = Popup(title='Uyarı',content=layout, auto_dismiss= False)
            pop.open()
            kapat.bind(on_press=pop.dismiss)
            
        elif ".com" not in self.url:
            popupLabel = Label(text = "Lütfen Uygun Bir Adres Girin!") 

            layout.add_widget(popupLabel)
            layout.add_widget(kapat)
            
            pop = Popup(title='Hata',content=layout, auto_dismiss= False)
            pop.open()
            kapat.bind(on_press=pop.dismiss)

        else:
            gorusler = self.Veri(self.url.strip())
            if len(gorusler) == 0:
                popupLabel = Label(text = "Seçilen Üründe Yorum Bulunmamaktadır!") 

                layout.add_widget(popupLabel)
                layout.add_widget(kapat)
                
                pop = Popup(title='Uyarı', content=layout, auto_dismiss= False)
                pop.open()
                kapat.bind(on_press=pop.dismiss)

            else:
                sonuc = self.Model(gorusler)        
                
                popupLabel = Label(text = "Yorum Sayısı: {}\nOlumluluk: %".format(len(gorusler)) + "%.2f" % sonuc) 
                popupLabel.font_size=13

                layout.add_widget(popupLabel)
                layout.add_widget(kapat)
                
                pop = Popup(title='Bilgi', content=layout, size_hint=(None, None), size=(300, 300), auto_dismiss= False)
                pop.open()
                kapat.bind(on_press=pop.dismiss)

    
ÜrünAnaliziApp().run()
