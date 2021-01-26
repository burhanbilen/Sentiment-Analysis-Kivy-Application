from nltk.corpus import stopwords
from bs4 import BeautifulSoup
import requests
import kivy
import re
import pickle
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from kivy.app import App
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.uix.pagelayout import PageLayout
from kivy.lang import Builder                                                                   
#from kivy.utils import platform                                                                 
#from kivy.uix.widget import Widget                                                              
#from kivy.clock import Clock                                                                    
#from jnius import autoclass                                                                     
#from android.runnable import run_on_ui_thread                                                   
Window.size = (300,480)

"""
WebView = autoclass('android.webkit.WebView')                                                   
WebViewClient = autoclass('android.webkit.WebViewClient')                                       
activity = autoclass('org.renpy.android.PythonActivity').mActivity                              

class Wv(Widget):                                                                               
    def __init__(self, **kwargs):                                                               
        super(Wv, self).__init__(**kwargs)                                                      
        Clock.schedule_once(self.create_webview, 0)            

    @run_on_ui_thread   
    def create_webview(self, *args):             
        webview = WebView(activity)
        webview.getSettings().setJavaScriptEnabled(True)                    
        wvc = WebViewClient();                                    
        webview.setWebViewClient(wvc);                                                          
        activity.setContentView(webview)                                                        
        webview.loadUrl('http://www.amazon.com')
class ServiceApp(App):                                                                          
    def build(self):                                                                            
        return Wv()  
"""
   
#Window.size = (300, 480)
kivy.require('1.9.0')

class MultipleLayout(PageLayout):
    pass
        
class ÜrünAnaliziApp(App):
    def build(self):
        return MultipleLayout()
    
    def process(self): 
        urun = self.root.ids.address.text 
        return urun
    
    def Temizle(self):
        self.root.ids.address.text  = ''
    
    def Analiz_animasyon(self, widget, *args):
        a = Animation(background_color=(1,2,0,1))
        a.start(widget)
        
    def Model(self, veri):
        df2 = pd.read_csv("bnn.csv")
        X = df2["Görüş"].values.astype('U')
        self.c = CountVectorizer()
        X = self.c.fit_transform(X)

        file_name = "mNB"
        loaded = pickle.load(open(file_name, 'rb'))
        yorumlar_vektor = self.c.transform(veri)
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
        kapat = Button(text='Tamam', on_press=self.Analiz_animasyon, size_hint=(25, None), size=(50, 30))
        kapat.font_size= 13

        if self.url.strip() == "":
            popupLabel = Label(text = "Lütfen Ürün Adresini Yazınız!") 
            popupLabel.font_size=13
            layout.add_widget(popupLabel)
            layout.add_widget(kapat)
            
            pop = Popup(title='Uyarı',content=layout, size_hint=(None, None), size=(200, 200), auto_dismiss= False)
            pop.open()
            kapat.bind(on_press=pop.dismiss)
            
        elif ".com" not in self.url:
            popupLabel = Label(text = "Lütfen Uygun Bir Adres Girin!") 
            popupLabel.font_size=13

            layout.add_widget(popupLabel)
            layout.add_widget(kapat)
            
            pop = Popup(title='Hata',content=layout, size_hint=(None, None), size=(200, 200), auto_dismiss= False)
            pop.open()
            kapat.bind(on_press=pop.dismiss)

        else:
            gorusler = self.Veri(self.url.strip())
            if len(gorusler) == 0:
                popupLabel = Label(text = "Seçilen Üründe Yorum Bulunmamaktadır!") 
                popupLabel.font_size=13

                layout.add_widget(popupLabel)
                layout.add_widget(kapat)
                
                pop = Popup(title='Uyarı',content=layout, size_hint=(None, None), size=(200, 200), auto_dismiss= False)
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

    
    
if __name__ == "__main__":  
    MlApp = ÜrünAnaliziApp() 
    MlApp.run()
