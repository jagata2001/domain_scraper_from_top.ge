import threading
import requests as r
from bs4 import BeautifulSoup
from queue import Queue
from time import sleep

class Topge:
    url = "https://top.ge"
    page_url = "https://top.ge/page/"
    def exception_decorator(func):
        def wrapper(self):
            try:
                func(self)
            except r.exceptions.ReadTimeout:
                print("Timeout error")
            except r.exceptions.ConnectionError:
                print("Connection error")
            except r.exceptions.SSLError:
                print("SSL error")
            #except:
            #    print("Something went wrong")

        return wrapper

    @exception_decorator
    def __init__(self):
        self.page_queue = Queue()
        self.domain_list = []

        respose = r.get(self.url)
        if respose.status_code == 200:
            soup = BeautifulSoup(respose.text,"html.parser")
            li_last_page = soup.find("li","page_nav last_page")
            last_page = li_last_page.find("a")
            last_page = last_page["href"].strip().split("/")[-1]
            for i in range(int(last_page)):
                self.page_queue.put(str(i))
        else:
            print(f"Status code error: {respose.status_code}")

    @exception_decorator
    def collect_domains(self):
        while self.page_queue.qsize() != 0:
            page = self.page_queue.get()
            response = r.get(self.page_url+page)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text,"html.parser")
                site_titles = soup.find_all("a",{"class":"stie_title"})
                for each in site_titles:
                    domain = each["href"].replace("www.","").replace("https://","").replace("http://","").split("/")[0]
                    self.domain_list.append(domain)
            else:
                print(f"Status code error: {respose.status_code}")




topge = Topge()
for _ in range(8):
    threading.Thread(target=topge.collect_domains).start()

while True:
    with open("domains.txt","w") as f:
        f.write(",".join(topge.domain_list))
        f.close()
    if threading.active_count() == 1:
        sleep(5)
        with open("domains.txt","w") as f:
            f.write(",".join(topge.domain_list))
            f.close()
        break
    print(len(topge.domain_list),threading.active_count(),topge.page_queue.qsize())
    sleep(2)
