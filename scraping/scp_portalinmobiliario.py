from scrapy.item import Field, Item
from scrapy.spiders import CrawlSpider, Rule
from scrapy.loader.processors import MapCompose
from scrapy.loader import ItemLoader
from scrapy.linkextractors import LinkExtractor
from scrapy.crawler import CrawlerProcess
from datetime import datetime
from unicodedata import normalize
import re

class Depto(Item) :
    titulo = Field()
    comuna = Field()
    ubicacion = Field()
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
    currency_symbol = Field()
    precio = Field()
    url = Field()

class PortainmobiliarioSpider(CrawlSpider) :
    # Nombre Spider
    name = "PortainmobiliarioSpider"
    # Configuraciones
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)Chrome/80.0.3987.149 Safari/537.36',
        # 'CLOSESPIDER_PAGECOUNT' : 2001,
        'FEED_EXPORT_ENCODING' : 'utf-8',
        # Tiempo de espera randomizado para cada requerimiento
        'RANDOMIZE_DOWNLOAD_DELAY' : True
    }
    # URls Semillas
    url = 'https://www.portalinmobiliario.com/arriendo/departamento/'
    #comunas = ['santiago', 'las-condes', 'la-reina', 'penalolen', 'la-florida', 'providencia', 'nunoa', 'macul']
    comunas = ['la-florida']
    metrop = '-metropolitana'
    start_urls = []
    for comuna in comunas : start_urls.append(url + comuna + metrop)
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
        return newText
    def deleteM2(self, text) :
        newText = text.replace(' m²', '')
        return newText
    def deleteCLP(self, text) :
        newText = text.replace(' CLP', '')
        return newText
    # Parsear dato departamentos
    def parse_depto(self, response) :
        item = ItemLoader(Depto(), response)
        item.add_xpath('titulo', '//h1[@class="ui-pdp-title"]/text()')
        item.add_xpath('comuna', '//ol/li[5]/a/text()')
        item.add_xpath('ubicacion', '//div[@class="ui-vip-location"]//p/text()')
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
        yield item.load_item()
# Deploy
path = 'scraping/output/'
now = datetime.now()
dt_string = now.strftime("%d-%m-%Yh%H.%M")
process = CrawlerProcess(settings={
    "FEEDS": {
        path + 'portainmobiliario_' + dt_string + '.csv' : {"format": "csv"},
    },
})
process.crawl(PortainmobiliarioSpider)
process.start()