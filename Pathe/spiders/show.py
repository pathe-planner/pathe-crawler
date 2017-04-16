from scrapy import Spider, Request
from Pathe.settings import *
from Pathe.items import Movie, Show
from Pathe.helpers import DateHelper, DataHelper

class ShowSpider(Spider):
    name = SHOW_NAME
    theaters = []

    def start_requests(self):
        base_url = SHOW_URL

        self.theaters = DataHelper(THEATER_FILE)
        theater_ids = self.theaters.to_string(self.theaters.get('id'))
        date = DateHelper.now()

        dateFlag = getattr(self, 'startdate', None)
        if dateFlag is not None: 
            date = DateHelper.strtodate(dateFlag)
            
        start_date = DateHelper.next_weekday(date, SHOW_CRAWL_DAY)
        end_date = DateHelper.add_days(start_date, SHOW_CRAWL_DAYS)

        for date in DateHelper.daterange(start_date, end_date):
            if date >= DateHelper.now():
                url = base_url + theater_ids + '/' + DateHelper.date(date)
                request = Request(url, self.parse)
                request.meta['date'] = DateHelper.date(date)
                yield request

    def parse(self, response):
        date = response.meta['date']

        for movieItem in response.css(SELECTORS['MOVIE_LIST']):
            movie = self.parse_movie(movieItem)
            
            for theaterItem in movieItem.css(SELECTORS['MOVIE_THEATER_LIST']):
                theater = self.theaters.search('name', self.get(theaterItem, SELECTORS['MOVIE_THEATER_NAME']))
                
                for showItem in theaterItem.css(SELECTORS['SHOW_LIST']):
                    show = self.parse_show(showItem, date, movie['id'], theater['id'])

    def parse_movie(self, response):
        obj = {
            'id': '',
            'title': self.get(response, SELECTORS['MOVIE_TITLE']),
            'description': self.get(response, SELECTORS['MOVIE_DESCRIPTION']), 
            'image': self.get(response, SELECTORS['MOVIE_IMAGE']), 
            'url': BASE_URL + self.get(response, SELECTORS['MOVIE_URL']),    
        }
        
        # store movie object
        return Movie(obj)

    def parse_show(self, response, date, movie_id, theater_id):
        obj = {
            'date': date, 
            'movie_id': movie_id,
            'theater_id': theater_id,
            'start': self.get(response, SELECTORS['SHOW_START']), 
            'end': '',
            'duration': '',
            'type': self.get(response, SELECTORS['SHOW_TYPE']),
            'url': BASE_URL + self.get(response, SELECTORS['SHOW_URL']),    
        }
        return Show(obj)

    def get(self, response, selector):
        return response.css(selector).extract_first()

