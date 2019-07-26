import os
import requests
from pyquery import PyQuery as query

import time
import json
import random

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'
}

img_urls_json_path = './img_urls.json'
urls_json_path = './urls.json'
group_json_path = './group.json'

img_path = 'H:\\image\\'

url = "http://www.ilemiss.net/e/search/result/index.php?page=0&searchid=590"

class pic_downloader():
    def __init__(self):
        self.img_dict = {}
        self.url_dict = {}
        self.group_dict = {}

    def start_request(self, url):
        try:
            r = requests.get(url, headers=headers)
            r.encoding = 'utf-8'
            html = r.text
            return html
        except:
            # any error occurs, retry
            time.sleep(5)
            return self.start_request(url)
        

    def parse_group(self, text):
        doc = query(text)
        lis = doc('.imbimg')
        for li in lis:
            content = query(li)
            a = content('a')
            ref = a.attr('href')
            if not self.group_dict.__contains__(ref):
                self.parse_img_url(ref)
                self.group_dict[ref] = ''
                with open(group_json_path,'w+', encoding='UTF-8') as outfile:
                    json.dump(self.group_dict, outfile, ensure_ascii=False)

        print("image url parsing all finished!")

    def parse_img_url(self, url):

        # parse base url
        base_url = url[0:url.index('.html')]

        text = self.start_request(url)
        doc = query(text)
        content = doc('.wlinkpages')

        # calc page count
        total_page = 0

        for c in content.children().items():
            if c.text() == "尾页":
                last_page = c.children().attr('href')
                total_page = int(last_page[last_page.index('_')+1:last_page.index('.')])

        x = 1

        while x <= total_page:
            new_url = ''
            if x == 1:
                new_url = url
            else:
                new_url = base_url + '_' + str(x) + '.html'

            if self.url_dict.__contains__(new_url):
                x += 1
                continue

            if new_url == url:
                # store image on current page
                content = doc('.contentpic')
                img_url = content.children().attr('src')
                img_name = content.children().attr('alt')
                self.img_dict[img_name] = img_url
            else:
                # request new page
                new_text = self.start_request(new_url)
                doc = query(new_text)
                content = doc('.contentpic')
                img_url = content.children().attr('src')
                img_name = content.children().attr('alt')
                self.img_dict[img_name] = img_url

            # record loaded urls
            self.url_dict[new_url] = ''
            x += 1
            print(new_url)

        # write dict to file
        with open(urls_json_path,'w+', encoding='UTF-8') as outfile:
            json.dump(self.url_dict, outfile, ensure_ascii=False)

        with open(img_urls_json_path,'w+', encoding='UTF-8') as outfile:
            json.dump(self.img_dict, outfile, ensure_ascii=False)

    def download(self):
        # load recorded image urls
        if os.path.exists(img_urls_json_path):
            with open(img_urls_json_path, 'r', encoding = 'UTF-8') as stored_file:
                img_dict = json.load(stored_file)

                pairs = img_dict.items()
                total = len(img_dict)
                x = 1
                for key, value in pairs:
                    path = img_path + str(key) + ".jpg"
                    
                    if not os.path.exists(path):
                        retry = 10
                        while retry > 0:
                            try:
                                print("downloding: " + str(x) + " in total: " + str(total))
                                img = requests.get(value, headers=headers).content
                                break
                            except:
                                time.sleep(3)
                                retry -= 1
                                if retry <= 0:
                                    print("Network Error!")
                                    return

                        with open(path, 'wb+') as f:
                            f.write(img)
                    
                    x += 1

    def begin(self):
        # initialize dicts
        if os.path.exists(group_json_path):
            with open(group_json_path, 'r', encoding='utf-8') as file:
                self.group_dict = json.load(file)

        if os.path.exists(urls_json_path):
            with open(urls_json_path, 'r', encoding='utf-8') as file:
                self.url_dict = json.load(file)

        if os.path.exists(img_urls_json_path):
            with open(img_urls_json_path, 'r', encoding='utf-8') as file:
                self.img_dict = json.load(file)

        text = self.start_request(url)
        self.parse_group(text)
        self.download()


