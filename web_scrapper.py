import aiohttp
from bs4 import BeautifulSoup
import pypeln as pl
import asyncio


class WebScraper:
    """
    This metaclass is designed for scraping any HTML data from a list of URLs.
    This class asynchronously processes each URL and fills the master dictionary with results.
    Modify the async def fetch() method to extract the needed data.
    """

    def __init__(self, urls: list, tcp_limit: int=10, workers: int=10, wait_time: int=30):
        """
        Args:
        ----
        urls: list
            list of URLs to process
        tcp_limit: int=10
            limit the number of connections the server can accept
        workers: int=10
            amount of simultaneous tasks
        wait_time: int=30
            time until the next request if the server response != 200.
        """
        self.headers = {'User-agent':
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582'
                        }
        self.urls = urls
        self.__master_dict = {}
        self.tcp_limit = tcp_limit
        self.workers = workers
        self.wait_time = wait_time

    def doc_search(self) -> None:
        """
        This method creates an asyncio loop, process the list of URLs and returns the results of the asynchronous scaping.
        
        Returns:
        self.result: dict
            the dict of the scrapped data.
        """
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        self.loop = asyncio.new_event_loop()
        self.result = self.loop.run_until_complete(self.price_scrap())
        self.loop.close()
        
        return self.result

    async def price_scrap(self) -> None:
        """
        This method creates an aiohttp session and calls the pl.task.each() method that runs the async method fetch() for each URL.
        This method searches for the data on each parsed HTML page.
        
        Returns:
        -------
        self.__master_dict: dict
            returns the hidden master dictionary with the HTML parsed results.
        """
        # Create the aiohttp session
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=self.tcp_limit)) as self.session:
            # Proceed all urls by fetch() method for parsing
            await pl.task.each(self.fetch, self.urls, workers=self.workers)
        return self.__master_dict

    async def fetch(self, url: str) -> None:
        """
        This method processes an URL, extracts the data from the parsed HTML and stores it in the master dictionary.
        
        Args:
        ----
        url: str
            a single URL to be scrapped.
        """
        while True:
            async with self.session.get(url, headers=self.headers) as response:
                self.__master_dict[url] = {}
                if response.status == 200:
                    page_html = await response.text()
                    # HTML parser
                    soup = BeautifulSoup(page_html, 'html.parser')
                    for i, doc in enumerate(soup.find_all('div', class_="prod-content")):
                        self.__master_dict[url][i+1] = {}
                        try:
                            # Insert here the parsing details
                            
                            # num = ' '.join(doc.find(
                            #     class_='title').get_text().split(' '))
                            # self.__master_dict[url][i+1]['article'] = num
                            pass
                        except (KeyError, AttributeError):
                            # self.__master_dict[url][i+1]['article'] = 'Undefined'
                            pass

                    break
                
                # If server response is not received, wait for {s} secondes and try again
                else:
                    print(f'Response status code: {response.status}')
                    print(f'Timeout for {self.wait_time} s')
                    await asyncio.sleep(self.wait_time)
                    continue
