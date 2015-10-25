from urllib import urlopen
from bs4 import BeautifulSoup
import mechanize
import re
import pyodbc
import cookielib
import schedule



def scrape_titles(url):
    soup=BeautifulSoup(url)
   # article_titles = [el.text for el in soup.findAll('a',"js-headline-text",href=re.compile('^http://www.theguardian.com/world/2015/'))]    
    #article_titles = [el.text for el in soup.select('h2 a[href^=/article/]')]
    article_titles = [el.text for el in soup.select('h3 a[href^=/doifinder]')]
    return article_titles

def scrape_articles(article_url):
    soup = BeautifulSoup(article_url)
   # articles = [el.text for el in soup.findAll('div',attrs={"data-test-id":"article-review-body"})]
    articles = [el.text for el in soup.findAll('section',attrs={"id":"article-body"})]
    return articles

def scrape_date_published(url):
    soup=BeautifulSoup(url)
    #article_date_published = [el.text for el in  soup.findAll('time')]
    article_date_published = [el.text for el in soup.select('.pubdate-and-corrections')]
    return article_date_published

def scrape_links(url):
    soup=BeautifulSoup(url)
   # links = [el['href'] for el in soup.findAll('a',"js-headline-text",href=re.compile('^http://www.theguardian.com/world/2015/'))]
    #links = [el['href'] for el in soup.select('h2 a[href^=/article/]')]
    links = ["http://www.nature.com"+el['href'] for el in soup.select('h3 a[href^=/doifinder]')]
    return links

def scrape_comments(url):
     soup=BeautifulSoup(url)
     comments = [el.text for el in soup.findAll('ol',attrs={"class":"comments-post-grapevine ugc"})]
     return comments

def main():
    conn = pyodbc.connect('DRIVER={HDBODBC32};SERVERNODE=localhost:30015;SERVERDB=SAPDB;UID=DEV_1TC7TGFJEAJYC5E15Y05JH64O;PWD=Ce3beNwNZxen2fD')
    cur = conn.cursor()
    br = mechanize.Browser()
    cj = cookielib.LWPCookieJar()      # Create cookiejar to handle cookies
    br.set_cookiejar(cj)               # Set cookie jar for our browser
    br.set_handle_equiv(True)          # Allow opening of certain files
    br.set_handle_gzip(True)           # Allow handling of zip files
    br.set_handle_redirect(True)       # Automatically handle auto-redirects
    br.set_handle_referer(True)
    br.set_handle_robots(False)        # ignore anti-robots.txt
 
    # Necessary headers to simulate an actual browser
    br.addheaders = [('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36'),
                   ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'),
                   ('Accept-Charset', 'ISO-8859-1,utf-8;q=0.7,*;q=0.3'),
                   ('Accept-Encoding', 'gzip,deflate,sdch'),
                   ('Accept-Language', 'en-US,en;q=0.8,fr;q=0.6'),
                   ('Connection', 'keep-alive')
                  ]
   # htmltext=br.open("https://news.vice.com/topic/politics/").get_data()
    htmltext=br.open("http://www.nature.com/news/top-content-article-page-7.799?tab=7.11333").get_data()
    titles = scrape_titles(htmltext)
    links = scrape_links(htmltext)
    article_date_published = []
    articles = []
    comments = []
    for link in links:
        data = br.open(link).get_data()    
        article_date_published.extend(scrape_date_published(data))
        articles.extend(scrape_articles(data))
        comments.extend(scrape_comments(data))


    all_info = map(lambda x,y,z,m,e:(x,y,z,m,e),titles,links,article_date_published,articles,comments)
    for row in all_info:
        try:
            cur.execute("INSERT INTO DEV_1TC7TGFJEAJYC5E15Y05JH64O.ARTICLES4 (Title,url,date_published,article_content,Comments) VALUES(?,?,?,?,?)",(row))
        except  Exception,ex:
            continue
    
    print "UEEE"
   # all_info = map(lambda x,y,z,m,e:(x,y,z,m,e),titles,links,articles,article_date_published,article_comments)     
  #  for row in all_info:
 #        cur.execute("INSERT INTO DEV_1TC7TGFJEAJYC5E15Y05JH64O.ARTICLES (Title,url,Article_content,date_published,Comments) VALUES(?,?,?,?,?)",(row))
         
    cur.execute("COMMIT")           
    cur.close()
if __name__ == "__main__":
    main()
    #schedule.every().day.at("18:15").do(main)
   # while True:
     #   schedule.run_pending()
        


    

