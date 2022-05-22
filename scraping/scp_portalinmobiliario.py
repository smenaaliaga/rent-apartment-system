from scrapy.item import Field, Item
from scrapy.spiders import CrawlSpider, Rule
from scrapy.loader import ItemLoader
from scrapy.linkextractors import LinkExtractor
from scrapy.crawler import CrawlerProcess
from itemloaders.processors import MapCompose
from datetime import datetime
from unicodedata import normalize
import re
import sys

comuna = sys.argv[1]

class Depto(Item) :
    titulo = Field()
    comuna = Field()
    direccion = Field()
    lat = Field()
    long = Field()
    estacion_cercana = Field()
    distancia_estacion = Field()
    descripcion = Field()
    superficie_total = Field()
    superficie_util = Field()
    dormitorios = Field()
    baños = Field()
    estacionamientos = Field()
    bodegas = Field()
    gastos_comunes = Field()
    search_gc = Field()
    currency_symbol = Field()
    precio = Field()
    url = Field()

class PortainmobiliarioSpider(CrawlSpider) :
    # Nombre Spider
    name = "PortainmobiliarioSpider"
    # Configuraciones
    now = datetime.now()
    dt_day = now.strftime("%d-%m-%Y")
    custom_settings = {
        # Identificación del sistema
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML like Gecko) Chrome/44.0.2403.155 Safari/537.36',
        # Encoding
        'FEED_EXPORT_ENCODING' : 'utf-8',
        # Tiempo de espera randomizado para cada requerimiento
        'RANDOMIZE_DOWNLOAD_DELAY' : True,
        # log
        'LOG_FILE' : 'scraping/log/portalinmobiliario_' + dt_day +'.txt',
        'LOG_LEVEL' : 'INFO',
        'LOG_STDOUT' : True,
        # Orden de los campos
        'FEED_EXPORT_FIELDS' : ['titulo','comuna','estacion_cercana','distancia_estacion','dormitorios','baños',
        'estacionamientos','bodegas','superficie_total','superficie_util','currency_symbol','precio','gastos_comunes',
        'search_gc','descripcion','direccion','lat','long','url']
    }
    # URls Semillas
    url = 'https://www.portalinmobiliario.com/arriendo/departamento/'
    metrop = '-metropolitana'
    start_urls = []
    start_urls.append(url + comuna + metrop)
    # Dominios permitidos
    allowed_domains = ['portalinmobiliario.com']
    # Regla para extraer los datos de la URLs
    rules = (
        # Horizontal
        Rule(LinkExtractor(
            allow = r'/_Desde_\d+',
            restrict_xpaths = r'//div[@class="ui-search-pagination"]'
        ), follow = True),
        # Vertical
        Rule(LinkExtractor(
                allow = r'/MLC-',
                restrict_xpaths = r'//section[@class="ui-search-results"]'
            ), follow = True, callback = 'parse_depto'),
    )
    # Preprocesamiento de datos
    def splitDistance(self, text) :
        newText = text.split(" - ")
        newText = newText[1].replace(' metros', '')
        return newText
    def lowerCaseNormalice(self, text) :
        newText = text.lower()
        newText = re.sub(
            r"([^n\u0300-\u036f]|n(?!\u0303(?![\u0300-\u036f])))[\u0300-\u036f]+", r"\1", 
            normalize( "NFD", newText), 0, re.I
        )
        newText = re.sub('[^a-zA-Z0-9 \.]', '', newText)
        newText = newText.replace('.', '')
        newText = re.sub(' +', ' ', newText)
        return newText
    def deleteM2(self, text) :
        newText = text.replace(' m²', '')
        return newText
    def deleteCLP(self, text) :
        newText = text.replace('.', '')
        newText = newText.replace(' CLP', '')
        return newText
    # Buscar en descripcion el precio del gasto comun
    def searchGastoComun(self, item) :
        precio = int(item.get_collected_values('precio')[0])
        desc_list = item.get_collected_values('descripcion')
        desc = ' '.join([str(elem) for elem in desc_list])
        list_gc = ['gastos comunes', 'gastos  comunes', 'gasto comun']
        bool = False
        for gc in list_gc :
            if gc in desc :
                i = desc.find(gc)
                text_aux = desc[(i-25 if i-25>0 else 0):(i+len(gc)+25 if i+len(gc)+25<=len(desc) else len(desc))]
                num_gc = [int(s) for s in re.findall(r'\b\d+\b', text_aux)]
                if len(num_gc) :
                    res = [i for i in num_gc if 10000 < i < precio]
                    if len(res) :
                        item.add_value('gastos_comunes', [str(res[0])])
                        item.add_value('search_gc', ['1'])
                        bool = True
                        break
        if bool == False : item.add_value('search_gc', ['0']) 
    # Parsear dato departamentos
    def parse_depto(self, response) :
        item = ItemLoader(Depto(), response)
        item.add_xpath('titulo', '//h1[@class="ui-pdp-title"]/text()')
        item.add_xpath('comuna', '//ol/li[5]/a/text()')
        item.add_xpath('direccion', '//div[@class="ui-vip-location"]//p/text()')
        # Split Lat Long
        def get_latlong(text) : 
            array = text.split('center=')
            array = array[1].split('&zoom')
            array = array[0].split('%2C')
            return array
        url_latlong = response.xpath('//img[@class="ui-pdp-image"]/@srcset').get()
        array_latlong = get_latlong(url_latlong)
        item.add_value('lat', array_latlong[0])
        item.add_value('long', array_latlong[1])
        item.add_xpath('estacion_cercana', 
        '//div[./span[contains(text(),"Estaciones")]]/div[@class="ui-vip-poi__item"][1]/div[@class="ui-vip-poi__item-title"]/span/text()')
        item.add_xpath('distancia_estacion', 
        '//div[./span[contains(text(),"Estaciones")]]/div[@class="ui-vip-poi__item"][1]/div[@class="ui-vip-poi__item-subtitle"]/span/text()',
        MapCompose(self.splitDistance))
        item.add_xpath('descripcion', '//p[@class="ui-pdp-description__content"]/text()',
        MapCompose(self.lowerCaseNormalice))
        item.add_xpath('superficie_total', '//tr[./th[contains(text(),"Superficie total")]]//span/text()',
        MapCompose(self.deleteM2))
        item.add_xpath('superficie_util', '//tr[./th[contains(text(),"Superficie útil")]]//span/text()',
        MapCompose(self.deleteM2))
        item.add_xpath('dormitorios', '//tr[./th[contains(text(),"Dormitorios")]]//span/text()')
        item.add_xpath('baños', '//tr[./th[contains(text(),"Baños")]]//span/text()')
        item.add_xpath('estacionamientos', '//tr[./th[contains(text(),"Estacionamientos")]]//span/text()')
        item.add_xpath('bodegas', '//tr[./th[contains(text(),"Bodegas")]]//span/text()')
        item.add_xpath('gastos_comunes', '//tr[./th[contains(text(),"Gastos comunes")]]//span/text()',
        MapCompose(self.deleteCLP))
        item.add_xpath('currency_symbol', '//span[@itemprop="priceCurrency"]/text()'),
        item.add_xpath('precio', '(//span[@class="andes-money-amount__fraction"])[last()]/text()',
        MapCompose(self.deleteCLP))
        item.add_value('url', response.request.url)
        # Revisión gastos comunes
        gastos_comunes = item.get_collected_values('gastos_comunes')
        if len(gastos_comunes) == 0 :
            self.searchGastoComun(item)
        else :
            item.add_value('search_gc', ['0'])
        yield item.load_item()
# Deploy
path = 'scraping/output/'
now = datetime.now()
dt_string = now.strftime("%d-%m-%Yh%H.%M")
process = CrawlerProcess(settings={
    "FEEDS": {
        path + 'portainmobiliario_' + comuna + '_' + dt_string + '.csv' : {"format": "csv"},
    },
})
process.crawl(PortainmobiliarioSpider)
process.start()