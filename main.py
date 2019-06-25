import re
import requests
from bs4 import BeautifulSoup
import re
from utorrentapi import UTorrentAPI
from selenium import webdriver
import time
import os

class TvboxnowDownloader:

    def __init__(self, topic_link):
        self.topic_link = topic_link
        driver = webdriver.Firefox(executable_path=r"PATH TO GECKODRIVER.EXE FILE")
        driver.get("http://www1.tvboxnow.com/logging.php?action=login&ref=%2Findex.php")
        time.sleep(2)
        element = driver.find_element_by_name('username')
        element.send_keys("Upworktest")
        element = driver.find_element_by_name('password')
        element.send_keys("Olegisthebest2019")
        driver.find_element_by_name("loginsubmit").click()
        time.sleep(3)
        self.DOWNLOAD_DIR = "PATH TO DOWNLOADS FOLDER"
        self.driver = driver

    def parse_forum_links(self, pages_count=1, links_on_topics_list = [], last_page=None):
        link = self.topic_link
        parse_link = f"{link.split('-')[0]}-{link.split('-')[1]}-{str(pages_count)}.html"
        forum_text = requests.get(parse_link)
        print(parse_link)

        if not last_page is None and pages_count > last_page:
            return links_on_topics_list
        forum_text = forum_text.text
        soup = BeautifulSoup(forum_text, 'lxml')
        if last_page is None:
            last_page_a = soup.find("a", class_='last')
            last_page = int(re.findall(r'... (\d+)', str(last_page_a))[0])
        for x in soup.find_all("table", class_='datatable'):
            for thread_links in re.findall(r'thread-\d+[-]1[-]\d.html', str(x)):
                links_on_topics_list.append(thread_links)

        return self.parse_forum_links(pages_count=pages_count+1, links_on_topics_list=links_on_topics_list,
                                      last_page=last_page)

    def parse_links_on_torrents(self):
        flag = True
        torrents_names_list = []
        driver = self.driver
        for thread_links in self.parse_forum_links():
            if flag:
                flag = False
                continue
            else:
                flag = True
            driver.get(f"http://www1.tvboxnow.com/{thread_links}")
            time.sleep(2)
            html = driver.page_source
            thread_soup = BeautifulSoup(html, 'lxml')
            for torrents in thread_soup.find_all("p", class_='attachname'):
                torrents_names_list.append({"text": torrents.a.text,
                                            "link": torrents.a['href']})
            if torrents_names_list:
                print('Please choose number of the torrent to download!')
                for i in range(len(torrents_names_list)):
                    print(f'{torrents_names_list[i]["text"]} {i + 1}')
                download_number = int(input()) - 1
                driver.get(f"http://www1.tvboxnow.com/{torrents_names_list[download_number]['link']}")
                time.sleep(5)
                torrents_names_list = []


    def filter_torrents(self, file):
        if 'torrent' in file.split("."):
            return 1
        else:
            return 0
    @staticmethod
    def torrent_download(torrent):
        api = UTorrentAPI("127.0.0.1:8080/gui", "admin", 'admin')
        api.add_file(f'{self.DOWNLOAD_DIR}/{torrent}')
    def list_torrents(self):
        for torrents in filter(self.filter_torrents, os.listdir(self.DOWNLOAD_DIR)):
            self.torrent_download(torrents)


tvboxnow = TvboxnowDownloader(input('URL of topic: '))
tvboxnow.parse_links_on_torrents()
tvboxnow.list_torrents()

