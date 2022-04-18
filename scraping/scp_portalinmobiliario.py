from scrapy.item import Field, Item
from scrapy.spiders import CrawlSpider, Rule
from scrapy.loader.processors import MapCompose
from scrapy.loader import ItemLoader
from scrapy.linkextractors import LinkExtractor
from scrapy.crawler import CrawlerProcess

class Depto(Item) :
    titulo = Field()
    ubicacion = Field()
    descripcion = Field()
    superficie_total = Field()
    superficie_util = Field()
    dormitorios = Field()
    baños = Field()
    estacionamiento = Field()
    gastos_comunes = Field()
    precio = Field()
    url = Field()

class PortainmobiliarioSpider(CrawlSpider) :
    # Nombre Spider
    name = "PortainmobiliarioSpider"
    # Configuraciones
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/71.0.3578.80 Chrome/71.0.3578.80 Safari/537.36',
        'CLOSESPIDER_PAGECOUNT' : 2001,
        'FEED_EXPORT_ENCODING' : 'utf-8'
    }
    # URls Semillas
    start_urls = [
        "https://www.portalinmobiliario.com/arriendo/departamento/santiago-metropolitana",  # Santiago Centro
        "https://www.portalinmobiliario.com/arriendo/departamento/providencia-metropolitana"# Providencia
        "https://www.portalinmobiliario.com/arriendo/departamento/penalolen-metropolitana", # Peñalolen
        "https://www.portalinmobiliario.com/arriendo/departamento/la-florida-metropolitana",# La Florida
        "https://www.portalinmobiliario.com/arriendo/departamento/las-condes-metropolitana",# Las Condes
        "https://www.portalinmobiliario.com/arriendo/departamento/la-reina-metropolitana",  # La Reina
        "https://www.portalinmobiliario.com/arriendo/departamento/macul-metropolitana",     # Macul
        "https://www.portalinmobiliario.com/arriendo/departamento/nunoa-metropolitana"      # Ñuñoa
        ]
    # Dominios permitidos
    allowed_domains = ['portalinmobiliario.com']
    # Tiempo de espera randomizado para cada requerimiento
    RANDOMIZE_DOWNLOAD_DELAY  = True
    # Regla para extraer los datos de la URL Senilla
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
    # Parsear dato departamentos
    def parse_depto(self, response) :
        item = ItemLoader(Depto(), response)
        item.add_xpath('titulo', '//h1[@class="ui-pdp-title"]/text()')
        item.add_xpath('ubicacion', '//div[@class="ui-vip-location"]//p/text()')
        item.add_xpath('descripcion', '//p[@class="ui-pdp-description__content"]/text()')
        item.add_xpath('superficie_total', '//tr[./th[contains(text(),"Superficie total")]]//span/text()',
        MapCompose(lambda i: i.replace(' m²', '')))
        item.add_xpath('superficie_util', '//tr[./th[contains(text(),"Superficie útil")]]//span/text()',
        MapCompose(lambda i: i.replace(' m²', '')))
        item.add_xpath('dormitorios', '//tr[./th[contains(text(),"Dormitorios")]]//span/text()')
        item.add_xpath('baños', '//tr[./th[contains(text(),"Baños")]]//span/text()')
        item.add_xpath('estacionamiento', '//tr[./th[contains(text(),"Estacionamientos")]]//span/text()')
        item.add_xpath('gastos_comunes', '//tr[./th[contains(text(),"Gastos comunes")]]//span/text()',
        MapCompose(lambda i: i.replace('.', '').replace(' CLP', '')))
        item.add_xpath('precio', '//span[@class="andes-money-amount__fraction"]/text()',
        MapCompose(lambda i: i.replace('.', '').replace(' CLP', '')))
        item.add_value('url', response.request.url)
        yield item.load_item()
# Deploy
process = CrawlerProcess({
        'FEED_FORMAT' : 'json',
        'FEED_URI' : 'scraping/output/portalinmobiliario.json'
    }
)
process.crawl(PortainmobiliarioSpider)
process.start()