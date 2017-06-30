# -*- encoding: utf-8 -*-

import os
import time
import random
import logging
import MySQLdb
import ConfigParser
import datetime
from selenium import webdriver


table_names = ['computercase','cpu','cpucooler','fan','graphicscard','hdd','memory','motherboard','powersupply','ssd']


cf = ConfigParser.ConfigParser()
cf.read("run.conf")



logging.basicConfig(level=logging.INFO,
                format='%(asctime)s %(filename)s[line:%(lineno)d] [%(levelname)s] %(message)s',
                datefmt='%a, %Y-%m-%d %H:%M:%S',
                filename=cf.get("log", "prefix") + "_" + str(datetime.date.today()) + '.txt',
                filemode='a')


def random_sleep():
    random_time = random.uniform(2,5);
    time.sleep(random_time)


def parse_price(driver, url, site_id):
    """
       tmall site_id=1
       jd    site_id=2
    """
    site_desc = ""
    if site_id == 1:
        site_desc = "天猫"
    elif site_id== 2:
        site_desc = "京东"

    #随机休眠一段时间
    random_sleep()

    logging.info("站点: " + site_desc + " 执行抓取: " + url)
    try:
        if site_id==1:
            driver.get(url)
            #促销价
            price_node = driver.find_element_by_css_selector('.tm-promo-price .tm-price')
            #原价
            if price_node is None:
                price_node = driver.find_element_by_css_selector('.tm-price')
            price = price_node.text
            # fix bug ERROR 'ascii' codec can't decode byte 0xe5 in position 0: ordinal not in range(128)
            logging.info(u"天猫价格: " + price)
            return price
        if site_id==2:
            driver.get(url)
            price_node = driver.find_element_by_css_selector('.p-price .price')
            price = price_node.text
            logging.info(u"京东价格: " + price)
            return price
    except Exception, e:
        logging.error("下载该页面失败,错误详情:")
        logging.error(e)
        return None


def crawl_10_tables(cursor):

    for table_name in table_names:

        # 统计每张表有价格的tmall和jd产品的数目
        tmall_price_count = 0
        jd_price_count = 0

        logging.info("\n")

        logging.info("开始抓取" + table_name + "表中的数据...");

        cursor.execute("select id, price3tmall, price4jingdong, price3link, price45link from " + table_name);

        items = cursor.fetchall();

        logging.info("从数据库" + table_name + "表中读取出" + str(len(items)) + "条数据, 共计抓取" + str(len(items) * 2) + "条url...");

        for item in items:
            try:
                _id = item[0]
                tmall_url = item[3]
                jingdong_url = item[4]
                tmall_price = parse_price(driver, tmall_url, 1)
                jd_price = parse_price(driver, jingdong_url, 2)
                try:
                    if tmall_price==None:
                        """do nothing"""
                    # float() argument must be a string or a number
                    elif(float(str(tmall_price))>0):
                        tmall_price_count += 1
                except Exception, e:
                    print e
                    """do nothing"""
                try:
                    if jd_price==None:
                        """do nothing"""
                    elif(float(str(jd_price))>0):
                        jd_price_count += 1
                except Exception, e:
                    print e
                    """do nothing"""

                try:
                    update_sql = "update cpu set price3tmall=%s, price4jingdong=%s, price345updatetime=%s where id=%s"

                    cursor.execute(update_sql, (tmall_price, jd_price, datetime.datetime.now() ,_id))

                except Exception, e:
                    logging.error("执行插入数据库语句失败:")
                    logging.error(e)

            except Exception, e:
                logging.error("未知异常")
                logging.error(e)
                logging.error("tmall_url: " + tmall_url)
                logging.error("jingdong_url: " + jingdong_url)


        logging.info("表" + table_name + "成功抓到天猫的价格个数: " + str(tmall_price_count) + " 成功抓到京东的价格个数: " + str(jd_price_count))
        logging.info("\n")


if __name__ == "__main__":


    # 为解决Chrome的httplib.BadStatusLine: ''问题
    # 版本57升级为58
    driver =  webdriver.Chrome()

    logging.info("初始化数据库连接...")
    
    conn = MySQLdb.connect(host=cf.get("db", "host"),
                           user=cf.get("db", "user"),
                           db=cf.get("db", "database"),
                           port=int(cf.get("db", "port")),
                           passwd=cf.get("db", "passwd"))

    #自动提交 没添加之前 存在没有保存的情况
    conn.autocommit(1)

    cursor = conn.cursor()

    #传入cursor 开始抓取十张表
    crawl_10_tables(cursor)

    driver.quit()

    if conn:
        logging.info("关闭数据库连接")
        conn.close()

    logging.info("程序执行完毕...")

    logging.info("\n\n")
    

    



