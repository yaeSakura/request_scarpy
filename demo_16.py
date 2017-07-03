#!/usr/bin/env python
# -*- coding:utf-8 -*-

import json
import requests
import time
import datetime

def fetch_stations(t, train_code, train_no, routes, fd):
    url = "https://kyfw.12306.cn/otn/czxx/queryByTrainNo"
    params = u"train_no=" + train_no + u"&from_station_telecode=BBB&to_station_telecode=BBB&depart_date=" + t
    try:
        s = requests.get(url, params=params.encode("utf-8"), verify=False)
    except Exception, e:
        print "fetch stations fail." + url
        raise e
    stations = json.loads(s.content)
    out = u"-----------------------------\n"
    out += train_code + u"\n"
    datas = stations["data"]["data"]
    size = len(datas)
    for i in range(0, size):
        A = datas[i]
        if i != size:
            for j in range(i + 1, size):
                B = datas[j]
                routes.add((A["station_name"], B["station_name"]))
        out += A["station_no"]
        out += u" " + A["station_name"]
        out += u" " + A["arrive_time"]
        out += u" " + A["start_time"]
        out += u" " + A["stopover_time"]
        out += u"\n"
    s = out.encode("utf-8")
    fd.write(s)
    fd.write("\n")
    fd.flush()
    print s

def fetch_all_train_list(routes):
    stations = fetch_stations_code()
    t = (datetime.datetime.now() + datetime.timedelta(days=3)).strftime("%Y-%m-%d")
    url = "https://kyfw.12306.cn/otn/queryTrainInfo/getTrainName"
    try:
        s = requests.get(url, params={"date":t}, verify=False)
    except Exception, e:
        print "requsts url fail.", url
        return
    datas = json.loads(s.content)
    with open("16.train_codes.txt", "w") as fd:
        fd.write(s.content)

    with open("16.train_infos.txt", "w") as fd:
        for data in datas["data"]:
            a = data["station_train_code"]
            b = a.split("(")[1]
            c1 = b.split("-")[0]
            c2 = b.split("-")[1].split(")")[0]
            size = len(stations)
            time.sleep(2)
            fetch_stations(t, data["station_train_code"], data["train_no"], routes, fd)
            for i in range(0, size):
                if c1 == stations[i][0]:
                    start_train_no = stations[i][1]
                if c2 == stations[i][0]:
                    end_train_no = stations[i][1]
            print c1, c2
            time.sleep(2)
            with open("16.train_price.txt", "w") as fd1:
                fetch_data(t, start_train_no, end_train_no, fd1)

def fetch_data(t, start, end, fd):

    url = "https://kyfw.12306.cn/otn/leftTicket/query"
    params = u"leftTicketDTO.train_date=" + t + u"&leftTicketDTO.from_station=" + start + u"&leftTicketDTO.to_station=" + end + u"&purpose_codes=ADULT"
    try:
        s = requests.get(url, params=params.encode("utf-8"), verify=False)
    except Exception, e:
        print "requests url fail.", url
        return
    datas = json.loads(s.content)
    if "result" not in datas["data"]:
        print "no train", t, start.encode("utf-8"), end.encode("utf-8")
        return
    for da in datas["data"]["result"]:
        data = {}
        time.sleep(2)
        data["from_station_name"] = da.split('|')[6]
        data["end_station_name"] = da.split('|')[7]
        data["station_train_code"] = da.split('|')[3]
        data["train_no"] = da.split('|')[2]
        # 余票数量信息
        data["swz_num"] = da.split('|')[-3]
        data["tz_num"] = da.split('|')[-10]
        data["zy_num"] = da.split('|')[-4]
        data["ze_num"] = da.split('|')[-5]
        data["gr_num"] = da.split('|')[-13]
        data["rw_num"] = da.split('|')[-12]
        data["yw_num"] = da.split('|')[-7]
        data["rz_num"] = da.split('|')[-8]
        data["yz_num"] = da.split('|')[-6]
        data["wz_num"] = da.split('|')[-9]
        data["qt_num"] = da.split('|')[-14]

        out = u"--------------------------------------\n"
        out += data["from_station_name"]
        out += u" " + data["end_station_name"]
        out += u" " + data["station_train_code"]
        out += u"\n" + data["swz_num"]  # 商务座     -3
        out += u" " + data["tz_num"]  # 特等座     -10
        out += u" " + data["zy_num"]  # 一等座     -4
        out += u" " + data["ze_num"]  # 二等座     -5
        out += u" " + data["gr_num"]  # 高级软卧    -13
        out += u" " + data["rw_num"]  # 软卧       -12
        out += u" " + data["yw_num"]  # 硬卧       -7
        out += u" " + data["rz_num"]  # 软座       -8
        out += u" " + data["yz_num"]  # 硬座       -6
        out += u" " + data["wz_num"]  # 无座      -9
        out += u" " + data["qt_num"]  # 其他       -14

        s = out.encode("utf-8")
        print s
        fd.write(s)
        fd.write("\n")
        # 要传给fetch_price的参数，fetch_price为余票价格信息
        data["from_station_no"] = da.split('|')[16]
        data["end_station_no"] = da.split('|')[17]
        data["seat_types"] = da.split('|')[-1]
        # code = data["station_train_code"]
        # src_name = data["from_station_name"]
        # des_name = data["end_station_name"]
        no = data["train_no"]
        time.sleep(2)
        fetch_price(t, data["from_station_no"], data["end_station_no"], no, data["seat_types"], fd)

def fetch_price(t, start, end, train_no, seat_types, fd):

        url = "https://kyfw.12306.cn/otn/leftTicket/queryTicketPrice"
        params = u"train_no=" + train_no + u"&from_station_no=" + start + u"&to_station_no=" + end + u"&seat_types=" + seat_types + u"&train_date=" + t
        try:
            s = requests.get(url, params=params.encode("utf-8"), verify=False)
        except Exception, e:
            print "fetch price fail. " + url
            raise e
        prices = json.loads(s.content)
        # print prices
        price = prices["data"]
        out = u""
        if "A9" in price:
            out += price["A9"]
        else:
            out += u" --"
        if "P" in price:
            out += u" " + price["P"]
        else:
            out += u" --"
        if "M" in price:
            out += u" " + price["M"]
        else:
            out += u" --"
        if "O" in price:
            out += u" " + price["O"]
        else:
            out += u" --"
        if "A6" in price:
            out += u" " + price["A6"]
        else:
            out += u" --"
        if "A4" in price:
            out += u" " + price["A4"]
        else:
            out += u" --"
        if "A3" in price:
            out += u" " + price["A3"]
        else:
            out += u" --"
        if "A2" in price:
            out += u" " + price["A2"]
        else:
            out += u" --"
        if "A1" in price:
            out += u" " + price["A1"]
        else:
            out += u" --"
        if "WZ" in price:
            out += u" " + price["WZ"]
        else:
            out += u" --"
        if "MIN" in price:
            out += u" " + price["MIN"]
        else:
            out += u" --"

        s = out.encode("utf-8")
        fd.write(s)
        fd.write("\n")
        fd.flush()
        print s

def store_routes(routes):
    with open("16.routes.txt", "w") as fd:
        for route in routes:
            out = route[0] + u" " + route[1] + u"\n"
            fd.write(out.encode("utf-8"))

def fetch_stations_code():
    url = "https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.8936"
    try:
        s = requests.get(url, verify=False)
    except Exception, e:
        print "fetch stations fail. " + url
        raise e
    station_str = s.content.decode("utf-8")
    stations = station_str.split(u"@")
    results = []
    for i in range(1, len(stations)):
        station = stations[i].split(u"|")
        results.append((station[1], station[2]))
    return results

if __name__ == "__main__":

    routes = set()
    fetch_all_train_list(routes)
    store_routes(routes)
