# coding=utf-8
import urllib
import re
from utils.mozie_request import Request
from hdvietnam.parser.category import Parser as Category
from hdvietnam.parser.channel import Parser as Channel
from hdvietnam.parser.movie import Parser as Movie
import utils.xbmc_helper as helper


class Hdvietnam:
    domain = "http://www.hdvietnam.com"

    def __init__(self):
        if not helper.getSetting('hdvietnam.username'):
            helper.message('Please login to hdvietnam.net', 'Login Required')

        self.request = Request(session=True)

    def login(self, redirect=None):
        params = {
            'login': helper.getSetting('hdvietnam.username'),
            'password': helper.getSetting('hdvietnam.password'),
            'register': 0,
            'cookie_check': 1,
            '_xfToken': '',
            'redirect': redirect
        }
        self.request.get('%s/login' % self.domain)
        response = self.request.post('%s/login/login' % self.domain, params)
        return response

    def thank(self, id, token, postLink):
        params = {
            '_xfRequestUri': id,
            '_xfToken': token,
            '_xfNoRedirect': 0,
            '_xfResponseType': 'json'
        }
        map(lambda v: self.request.post('%s/%s' % (self.domain, v), params), postLink)

    def getCategory(self):
        return Category().get()

    def getChannel(self, channel, page=1):
        channel = channel.replace(self.domain, "")
        if page > 1:
            url = '%s%spage-%d' % (self.domain, channel, page)
        else:
            url = '%s%s' % (self.domain, channel)
        response = Request().get(url)
        return Channel().get(response, page)

    def getMovie(self, id):
        url = '%s/%s' % (self.domain, id)
        print(url)
        response = self.login(redirect=url)
        parser = Movie()
        result, postLinks = parser.is_block(response)
        if result is True:
            token = re.findall(r'name="_xfToken"\svalue="(.*?)"\s', response)
            self.thank(id, token[0], postLinks)
            response = self.request.get(url)

        result = parser.get(response)
        return result

    def search(self, text):
        text = urllib.quote_plus(text)
        url = "%s/wp-admin/admin-ajax.php" % self.domain
        response = Request().post(url, params={
            'action': 'ajaxsearchpro_search',
            'asid': 1,
            'asp_inst_id': '1_1',
            'aspp': text,
            'options': 'current_page_id=64113&qtranslate_lang=0&asp_gen%5B%5D=title&asp_gen%5B%5D=content&customset%5B%5D=page&customset%5B%5D=post'
        })
        return Channel().search_result(response)
