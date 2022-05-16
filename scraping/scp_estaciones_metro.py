from scrapy.item import Field, Item
from scrapy.spiders import CrawlSpider, Rule
from scrapy.loader.processors import MapCompose
from scrapy.loader import ItemLoader
from scrapy.linkextractors import LinkExtractor
from scrapy.crawler import CrawlerProcess

class Estacion(Item) :
    nombre = Field()
    lat = Field()
    long = Field()
    
class LatLongEstaciones(CrawlSpider) :
    name = "LatLongEstaciones"
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/71.0.3578.80 Chrome/71.0.3578.80 Safari/537.36'
    }
    start_urls = [
        'https://es.wikipedia.org/wiki/Línea_1_del_Metro_de_Santiago', 
        'https://es.wikipedia.org/wiki/Línea_2_del_Metro_de_Santiago', 
        'https://es.wikipedia.org/wiki/Línea_3_del_Metro_de_Santiago',
        'https://es.wikipedia.org/wiki/Línea_4_del_Metro_de_Santiago',
        'https://es.wikipedia.org/wiki/Línea_4A_del_Metro_de_Santiago',
        'https://es.wikipedia.org/wiki/Línea_5_del_Metro_de_Santiago',
        'https://es.wikipedia.org/wiki/Línea_6_del_Metro_de_Santiago'
        ]
    RANDOMIZE_DOWNLOAD_DELAY  = True
    rules = (
        Rule(
            LinkExtractor(
                allow = r'/wiki/',
                attrs = ('href'),
                restrict_xpaths = (
                    '//div[@class="mw-parser-output"]//tr/td[@style="text-align:center;"]/table')
            ), callback = 'parse_estacion' 
        ),
    )

    def parse_estacion(self, response) :
        item = ItemLoader(Estacion(), response)
        item.add_xpath('nombre', '//tr/th[@class="cabecera"]/text()')
        item.add_xpath('lat','(//span[@class="geo"]/span[@class="latitude"]/text())[1]',
        MapCompose(lambda i: i.replace(', ', '')))
        item.add_xpath('long','(//span[@class="geo"]/span[@class="longitude"]/text())[1]')

        yield item.load_item()

# Deploy
path = 'scraping/output/'
process = CrawlerProcess(settings={
    "FEEDS": {
        path + 'estaciones.csv' : {"format": "csv"},
    },
})
process.crawl(LatLongEstaciones)
process.start()
# EJECUCION EN TERMINAL:
# scrapy runspider nivel2_estaciones.py -o results/estaciones.csv -t csv