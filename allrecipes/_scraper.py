# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup

import urllib.parse
import urllib.request

import re


class AllRecipes(object):
    @staticmethod
    def search(query_dict):
        """
        Search recipes parsing the returned html data.
        """
        base_url = "https://allrecipes.com/search/results/?"
        query_url = urllib.parse.urlencode(query_dict)

        url = base_url + query_url

        req = urllib.request.Request(url)
        req.add_header('Cookie', 'euConsent=true')

        html_content = urllib.request.urlopen(req).read()

        soup = BeautifulSoup(html_content, 'html.parser')

        search_data = []
        articles = soup.findAll("article", {"class": "fixed-recipe-card"})

        iterarticles = iter(articles)
        next(iterarticles)
        for article in iterarticles:
            data = {}
            try:
                data["name"] = article.find("h3", {"class": "fixed-recipe-card__h3"}).get_text().strip(' \t\n\r')
                data["description"] = article.find("div", {"class": "fixed-recipe-card__description"}).get_text().strip(
                    ' \t\n\r')
                data["url"] = article.find("a", href=re.compile('^https://www.allrecipes.com/recipe/'))['href']
                try:
                    data["image"] = \
                        article.find("a", href=re.compile('^https://www.allrecipes.com/recipe/')).find("img")[
                            "data-original-src"]
                except Exception as e1:
                    pass
            except Exception as e2:
                pass
            if data and "image" in data:  # Do not include if no image -> its probably an ad or something you do not want in your result
                search_data.append(data)

        return search_data

    @staticmethod
    def get(url):
        """
        'url' from 'search' method.
         ex. "/recipe/106349/beef-and-spinach-curry/"
        """
        # base_url = "https://allrecipes.com/"
        # url = base_url + uri

        req = urllib.request.Request(url + "?printview")
        req.add_header('Cookie', 'euConsent=true')

        html_content = urllib.request.urlopen(req).read()
        soup = BeautifulSoup(html_content, 'html.parser')

        unformatted_ingredients = [
            element.text for element in soup.findAll('span', {"class": "ingredients-item-name"})
        ]
        ingredients = [
            ingredient[51:len(ingredient)].split("\n")[0] for ingredient in unformatted_ingredients
        ]

        unformatted_directions = [
            element.text for element in soup.findAll("li", {"class": "subcontainer instructions-section-item"})
        ]

        def format(_list):
            for index in range(len(_list)):
                element = _list[index]
                for char_index in range(len(element)):
                    if element[char_index] != " ":
                        _list[index] = element[char_index:]
                        break
            for index in range(len(_list)):
                if '                  ' in _list[index]:
                    _list[index] = ''

            while _list.__contains__(''):
                _list.remove('')
            while _list.__contains__('Advertisement'):
                _list.remove('Advertisement')

            return _list

        directions = [
            tuple(format(direction.split("\n"))) for direction in unformatted_directions
        ]

        unformatted_serving_info = [
            element.text for element in soup.findAll("div", {"class": "partial recipe-nutrition-section"})
        ]
        serving_info = [
            tuple(format(info.split("\n"))) for info in unformatted_serving_info
        ]
        serving_info = list(serving_info[0])
        serving_info += format(serving_info[1].split(";"))
        serving_info.pop(1)

        if "  Full Nutrition" in serving_info[-1]:
            serving_info.pop(-1)
        elif "Full Nutrition" in serving_info[-1]:
            serving_info.pop(-1)

        for info_index in range(len(serving_info)):
            if '        ' in serving_info[info_index]:
                serving_info.append(serving_info[info_index].split('      ')[1])
                serving_info[info_index] = serving_info[info_index].split('      ')[0]

        serving_info = {serving_info[0]: serving_info[1:]}

        unformatted_recipe_time = [element.text for element in soup.findAll("div", {"class": "recipe-meta-item"})]
        recipe_times = [tuple(format(time.split('\n'))) for time in unformatted_recipe_time]

        return {
            "ingredients": ingredients,
            "directions": directions,
            "nutrition": serving_info,
            "recipe_time": recipe_times
        }
