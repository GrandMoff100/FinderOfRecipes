from allrecipes import AllRecipes as allrecipes_scraper


class Recipe:
    def __init__(self, recipe_dict):
        self.name = recipe_dict["name"]
        self.url = recipe_dict["url"]
        self.image = recipe_dict["image"]
        self.description = recipe_dict["description"]
        detailed_info = allrecipes_scraper.get(self.url)
        for attr in detailed_info:
            self.__setattr__(attr, detailed_info[attr])

    def __repr__(self):
        return str({attr: self.__getattribute__(attr) for attr in
                    ['name', 'url', 'image', 'description', 'ingredients', 'directions', 'nutrition', 'recipe_time']})

    def __dict__(self):
        return {attr: self.__getattribute__(attr) for attr in
                ['name', 'url', 'image', 'description', 'ingredients', 'directions', 'nutrition', 'recipe_time']}

    def __getitem__(self, item):
        if item in dir(self):
            return self.__getattribute__(item)
        else:
            raise KeyError("Object Recipe has no attribute {}".format(item))


def scrapeRecipes(includeIngredients=None, excludeIngredients=None, sort=None):
    query_params = {}
    if includeIngredients:
        query_params["ingIncl"] = includeIngredients

    if excludeIngredients:
        query_params["ingExcl"] = excludeIngredients

    if sort:
        if sort not in ["re", "ra", "p"]:
            raise ValueError("Not valid sorting type, only re (relevance), ra (rating), p (popular) accepted.")
        query_params["sort"] = sort

    return allrecipes_scraper.search(query_params)
