import os
import requests
from pyquery import PyQuery as pq

import time

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'
}

def start_request(url):
    try:
        r = requests.get(url, headers=headers)
        r.encoding = 'utf-8'
        html = r.text
        return html
    except requests.exceptions.ConnectionError:
        print("connect fail")
    except requests.exceptions.RetryError:
        print("retry failed")
        time.sleep(5)
        return start_request(url)
    except:
        print("unknown error occurred")

def download(text, count):
    while True:
        doc = pq(text)
        content = doc('.contentpic')
        img_url = content.children().attr('src')
        img_name = content.children().attr('alt')

        # print("Downloding:" + img_name)
        count += 1
        print(count)
        # path = "F:\\image\\" + str(img_name) + ".jpg"
        
        # if not os.path.exists(path):
        #     img = requests.get(img_url, headers=headers).content
        #     with open(path, 'wb+') as f:
        #         f.write(img)
        #         time.sleep(1)

        nextPage = doc('.nextpage')
        
        if nextPage.children().attr('href') is None:
            print("Group Done")
            return count
        else:
            time.sleep(1)
            next_url = 'http://www.ilemiss.net/sexy/' + nextPage.children().attr('href')
            text = start_request(next_url)

def parse(text):
    doc = pq(text)

    lis = doc('.imbimg')
    total = 0
    for li in lis:
        content = pq(li)
        a = content('a')
        ref = a.attr('href')
        total += download(start_request(ref), total)
        print(total)

def main():
    url = "http://www.ilemiss.net/e/search/result/index.php?page=0&searchid=590"
    text = start_request(url)

    parse(text)
    #download(text)


if __name__ == "__main__":
    main()