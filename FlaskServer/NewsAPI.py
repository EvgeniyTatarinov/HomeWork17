from concurrent.futures import ThreadPoolExecutor, as_completed
import requests


class publication:
    """
    :param API_KEY: your API key
    :return json object
    You can change the following settings:
    pageSize: The number of results to return per page [type(int)]
    page: page number [type(int)]
    language: code of the language
    country: code country
    """
    def __init__(self, API_KEY):
        self.key = API_KEY
        self.pageSize = 20
        self.page = 1
        self.language = 'ru'
        self.country = 'ru'

    def publication_of_categories(self, category):
        """
        Recent publications on the list of categories
        """
        response = requests.get('https://newsapi.org/v2/top-headlines?'
                                f'category={category}&'
                                f'language={self.language}&'
                                f'country={self.country}',
                                headers={'Authorization': self.key})
        return response.json()

    def publications_of_keywords(self, search):
        """
        Search for publications on request
        """
        response = requests.get('https://newsapi.org/v2/everything?'
                                f'q={search}&'
                                'sortBy=relevancy&'
                                f'language={self.language}',
                                headers={'Authorization': self.key})
        return response.json()


def pool_news(api, list_values, funk='categories'):
    """
    Search across multiple categories
    :param list_value: pass categories as a list
    :param funk: An executable function (keywords OR categories)
    :return: json object {[the name of the category]:{}}
    """
    with ThreadPoolExecutor() as pool:
        news = publication(api)
        if funk == 'keywords':
            list_requests = [
                pool.submit(news.publications_of_keywords, value)
                for value in list_values
            ]
        else:
            list_requests = [
                pool.submit(news.publication_of_categories, value)
                for value in list_values
            ]
        preliminary_result = {}
        for list_news in as_completed(list_requests):
            print(list_news.result())
            res = list_news.result()
            for news in list_values:
                print(news)
                preliminary_result[news] = res

    result = {}
    for parse in preliminary_result:
        result[parse] = [(n["title"], f'{n["description"]}...', n["url"])
                         for n in preliminary_result[parse]['articles']][:10]
    return result

