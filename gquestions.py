usage='''
❓❔👾 Gquestions CLI Usage ❔❓

🔍 Usage:
    gquestions.py query <keyword> (en|es) [depth <depth>] [--csv] [--headless]
    gquestions.py (-h | --help)

💡 Examples:
    ▶️  gquestions.py query "flights" en              Search "flights" in English and export in html
    ▶️  gquestions.py query "flights" en --headless   Search headlessly "flights" in English and export in html
    ▶️  gquestions.py query "vuelos" es --csv         Search "vuelos" in Spanish and export in html and csv
    ▶️  gquestions.py query "vuelos" es depth 1       Search "vuelos" in Spanish with a depth of 1 and export in html
    ▶️  gquestions.py -h                              Print this message
   
👀 Options:
    -h, --help

'''

import os
import re
import sys
import json
import time
import datetime
import platform
from docopt import docopt
from tqdm import tqdm 
from time import sleep
import pandas as pd
from pandas.io.json import json_normalize
import logging
from jinja2 import Environment, FileSystemLoader

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException

''' 
Visualizza una barra di caricamento per mostrare l'attesa
'''
def sleepBar(seconds):
    for i in tqdm(range(seconds)):
        sleep(1)

def prettyOutputName(filetype='html'):
    _query = re.sub('\s|\"|\/|\:|\.','_', query.rstrip())
    prettyname = _query
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%Y_%H-%M-%S-%f')
    if filetype != 'html':
        prettyname += "_" + st + "." + filetype
    else:
        prettyname += "_" + st + "." + filetype
    return prettyname


def initBrowser(headless=False):
    if "Windows" in platform.system():
        chrome_path = "driver/chromedriver.exe"
    else:
        chrome_path = "driver/chromedriver"
    chrome_options = Options()
    chrome_options.add_argument("--disable-features=NetworkService")
    if headless:
        chrome_options.add_argument('headless')
    return webdriver.Chrome(options=chrome_options,executable_path=chrome_path)
"""
Search on Google and returns the list of PAA questions in SERP.
"""
def newSearch(browser,query):
    if lang== "en":
        browser.get("https://www.google.com?hl=en")
        searchbox = browser.find_element_by_xpath("//input[@aria-label='Search']")
    else:
        browser.get("https://www.google.com?hl=es")
        searchbox = browser.find_element_by_xpath("//input[@aria-label='Buscar']")
    
    searchbox.send_keys(query)
    sleepBar(2)
    tabNTimes()
    if lang== "en":
        searchbtn = browser.find_elements_by_xpath("//input[@aria-label='Google Search']")
    else:
    	searchbtn = browser.find_elements_by_xpath("//input[@aria-label='Buscar con Google']")
    try:
        searchbtn[-1].click()
    except:
        searchbtn[0].click()
    sleepBar(2)
    paa = browser.find_elements_by_xpath("//span/following-sibling::div[contains(@class,'match-mod-horizontal-padding')]")
    hideGBar()
    return paa
"""
Helper function that scroll into view the PAA questions element.
"""
def scrollToFeedback():
    if lang == "en":
        el = browser.find_element_by_xpath("//div[@class='kno-ftr']//div/following-sibling::a[text()='Feedback']")
    else:
    	el = browser.find_element_by_xpath("//div[@class='kno-ftr']//div/following-sibling::a[text()='Enviar comentarios']")

    actions = ActionChains(browser)
    actions.move_to_element(el).perform()
    browser.execute_script("arguments[0].scrollIntoView();", el)
    actions.send_keys(Keys.PAGE_UP).perform()
    sleepBar(1)
"""
Accessibility helper: press TAB N times (default 2)
"""
def tabNTimes(N=2):
    actions = ActionChains(browser) 
    for _ in range(N):
        actions = actions.send_keys(Keys.TAB)
    actions.perform()

"""
Click on questions N times
"""
def clickNTimes(el, n=1):
    for i in range(n):
        el.click()
        logging.info(f"clicking on ... {el.text}")
        sleepBar(1)
        scrollToFeedback()
        try:
            el.find_element_by_xpath("//*[@aria-expanded='true']").click()
        except:
            pass
        sleepBar(1)

"""
Hide Google Bar to prevent ClickInterceptionError
"""
def hideGBar():
	try:
		browser.execute_script('document.getElementById("searchform").style.display = "none";')
	except:
		pass

"""
Where the magic happens
"""
def crawlQuestions(start_paa, paa_list, initialSet, depth=0):
    _tmp = createNode(paa_lst=paa_list, name=query, children=True)
    
    outer_cnt = 0
    for q in start_paa:
        scrollToFeedback()
        if "Dictionary" in q.text:
            continue
        test = createNode(paa_lst=paa_list, n=0,
                        name=q.text,
                        parent=paa_list[0]["name"],
                        children=True)
        
        clickNTimes(q)
        new_q = showNewQuestions(initialSet)
        for l, value in new_q.items():
            sleepBar(1)
            logging.info(f"{l}, {value.text}")
            test1 = createNode(paa_lst=test[0]["children"][outer_cnt]["children"], 
                                name=value.text,
                                parent=test[0]["children"][outer_cnt]["name"],
                                children=True)
            
        initialSet = getCurrentSERP()
        logging.info(f"Current count: {outer_cnt}")
        outer_cnt += 1
        if depth==1:
            for i in range(depth):
                currentQuestions = []
                for i in initialSet.values():
                    currentQuestions.append(i.text)
                for i in paa_list[0]["children"]:
                    for j in i["children"]:
                        parent = j['name']
                        logging.info(parent)
                        _tmpset = set()
                        if parent in currentQuestions:
                            try:
                                if "'" in parent:
                                    xpath_compiler = '//div[text()="' + parent + '"]'
                                else: 
                                    xpath_compiler= "//div[text()='" + parent + "']"
                                question= browser.find_element_by_xpath(xpath_compiler)
                            except NoSuchElementException:
                                continue
                            scrollToFeedback()
                            sleepBar(1)
                            clickNTimes(question)
                            new_q = showNewQuestions(initialSet)
                            for l, value in new_q.items():
                                if value.text == parent:
                                    continue
                                j['children'].append({"name": value.text,"parent": parent})
                                
                            initialSet = getCurrentSERP()

"""
Get the current Result Page.

Returns: 
    A list with newest questions.

"""
def getCurrentSERP():
    _tmpset = {}
    new_paa = browser.find_elements_by_xpath("//span/following-sibling::div[contains(@class,'match-mod-horizontal-padding')]")
    cnt= 0
    for q in new_paa:
        _tmpset.update({cnt:q})
        cnt +=1
    newInitialSet = _tmpset
    return newInitialSet

"""
Shows new questions.

Args:
    intialSet (dict): The initial set in the PAA box.
Returns:
    list of questions with first 3-4 questions deleted (initalSet).
"""
def showNewQuestions(initialSet):
    tmp = getCurrentSERP()
    deletelist = [k for k, v in initialSet.items() if k in tmp and tmp[k] == v]
    _tst = dict.copy(tmp)
    for i,value in tmp.items():
        if i in deletelist:
            _tst.pop(i)
    return _tst

"""
Create a new node in the list.

Args:
    paa_list_elements: list of web elements
    n: index of 'children' list on a main node
    name: node nome
    parent: Indicates if the node has a parent. Default to null only for first level.
    chilren: Indicates if the node has a children list. default false

Returns:
    list of questions with the current new node
"""
def createNode( n=-1, parent='null', children=False, name='',*, paa_lst):
    logging.info(paa_lst)
    if children:
        _d = {
        "name": name,
        "parent": parent,
        "children": [] 
        }
    else:
        _d = {
        "name": name,
        "parent": parent
        }
    if n!=-1:
        logging.info(paa_lst[n]["children"])
        paa_lst[n]["children"].append(_d)
    else:
        paa_lst.append(_d)
    

    return paa_lst

"""
This func takes in input JSON data and returns csv file.
"""
def flatten_csv(data,depth,prettyname):
    try:
        if depth == 0:
            _ = json_normalize(data[0]["children"], 'children', ['name', 'parent',['children',]], record_prefix='inner.')
            _.drop(columns=['children','inner.children','inner.parent'], inplace=True)
            columnTitle = ['parent','name','inner.name']
            _ = _.reindex(columns=columnTitle)
            _.to_csv(prettyname,sep=";",encoding='utf-8')
        elif depth == 1:
            df = json_normalize(data[0]["children"], meta=['name','children','parent'], record_path="children", record_prefix='inner.')
            frames = [ json_normalize(i) for i in df['inner.children'] ]
            result = pd.concat(frames)
            result.rename(columns={"name": "inner.inner.name", "parent": "inner.name"}, inplace=True)
            merge = pd.merge(df, result, how='left', on="inner.name")
            merge.drop(columns=['name'], inplace=True)
            columnTitle = ['parent','inner.parent','inner.name','inner.inner.name']
            merge = merge.reindex(columns=columnTitle)
            merge = merge.drop_duplicates(subset='inner.inner.name', keep='first')
            merge.to_csv(prettyname,sep=';',encoding='utf-8')
    except Exception as e:
        logging.warning(f"{e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    args = docopt(usage)
    print(args)
    MAX_DEPTH = 1

    if args['<depth>']:
        depth = int(args['<depth>'])
        if depth > MAX_DEPTH:
            sys.exit("depth not allowed")
    else:
        depth = 0

    if args['en']:
        lang = "en"
    elif args['es']:
        lang = "es"
        


    if args['<keyword>']:
        if args['--headless']:
            browser = initBrowser(True)
        else:
            browser = initBrowser()
        query = args['<keyword>']
        start_paa = newSearch(browser,query)

        initialSet = {}
        cnt= 0
        for q in start_paa:
            initialSet.update({cnt:q})
            cnt +=1

        paa_list = []

        crawlQuestions(start_paa, paa_list, initialSet,depth)
        treeData = 'var treeData = ' + json.dumps(paa_list) + ';'
        
        if paa_list[0]['children']:
            root = os.path.dirname(os.path.abspath(__file__))
            templates_dir = os.path.join(root, 'templates')
            env = Environment( loader = FileSystemLoader(templates_dir) )
            template = env.get_template('index.html')
            filename = os.path.join(root, 'html', prettyOutputName())
            with open(filename, 'w') as fh:
                fh.write(template.render(
                    treeData = treeData,
                ))

    if args['--csv']:
        if paa_list[0]['children']:
            _path = 'csv/'+prettyOutputName('csv')
            flatten_csv(paa_list, depth, _path)

    browser.close()