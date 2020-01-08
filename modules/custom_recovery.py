#!/usr/bin/env python3.7
"""custom recovery downloads scraper"""

import xml.etree.ElementTree as eT
from bs4 import BeautifulSoup
from collections import OrderedDict
from requests import get
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from .extras import check_codename
from .mwt import MWT


@MWT(timeout=60 * 60 * 6)
def load_twrp_data():
    """
    load devices info every six hours
    :returns sorted_data
    """
    data = {}
    response = get('https://twrp.me/Devices/Xiaomi/')
    page = BeautifulSoup(response.content, 'html.parser')
    devices = page.find("ul", {"class": "post-list"}).findAll('a')
    for i in devices:
        info = {}
        codename = i.text.split('(')[-1].split(')')[0]
        if '/' in codename:
            codename = codename.split('/')[0]
        link = f'https://dl.twrp.me/{codename}/'
        device = i.text
        info.update({'name': device})
        info.update({'link': link})
        data.update({codename: info})
    sorted_data = OrderedDict(sorted(data.items()))
    return sorted_data


@MWT(timeout=60 * 60 * 6)
def twrp(device):
    """
    fetch latest twrp links for a device
    :argument device - Xiaomi device codename
    :returns message - telegram message string
    :returns status - Boolean for device status whether found or not
    """
    status = None
    reply_markup = None
    data = load_twrp_data()
    if device not in list(data.keys()):
        message = f"Can't find downloads for {device}!"
        status = False
        return message, status, reply_markup
    name = data[device]['name']
    link = data[device]['link']
    page = BeautifulSoup(get(link).content, 'html.parser').find('table').find('tr')
    download = page.find('a')
    dl_link = f"https://dl.twrp.me{download['href']}"
    dl_file = download.text
    size = page.find("span", {"class": "filesize"}).text
    date = page.find("em").text.strip()
    message = f'*Latest TWRP for {name}:*\n' \
              f'*Updated:* {date}\n'
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(f"{dl_file} - {size}", url=dl_link)]])
    return message, status, reply_markup


@MWT(timeout=60 * 60 * 6)
def load_pbrp_data():
    """
    load latest xml files every six hours
    :returns data
    """
    rss = get(
        "https://sourceforge.net/projects/pitchblack-twrp/rss?path=/").text
    data = eT.fromstring(rss)
    return data


@MWT(timeout=60 * 60 * 6)
def pbrp(device):
    """
    fetch latest pbrp links for a device
    :argument device - Xiaomi device codename
    :returns message - telegram message string
    :returns status - Boolean for device status whether found or not
    """
    data = load_pbrp_data()
    reply_markup = None
    links = [i.find('link').text for i in data[0].findall('item')]
    try:
        link = [i for i in links if device in i][0]
    except IndexError:
        message = f"Can't find downloads for {device}!"
        status = False
        return message, status, reply_markup
    file = link.split('/')[-2]
    message = f'Latest [PitchBlack](https://pbrp.ml) Build for `{device}`:\n'
    status = True
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(file, url=link)]])
    return message, status, reply_markup


@MWT(timeout=60 * 60 * 2)
def load_ofrp_data():
    """
    load latest json file every six hours
    :returns data
    """
    return get("https://files.orangefox.tech/Other/update_v2.json").json()


@MWT(timeout=60 * 60 * 2)
def ofrp(device):
    """
    fetch latest ofrp links for a device
    :argument device - Xiaomi device codename
    :returns message - telegram message string
    :returns status - Boolean for device status whether found or not
    """
    data = load_ofrp_data()
    reply_markup = None
    url = f'https://files.orangefox.tech/OrangeFox'
    try:
        info = data[device]
    except KeyError:
        message = f"Can't find downloads for {device}!"
        status = False
        return message, status, reply_markup
    has_beta = False
    name = info['fullname']
    maintainer = info['maintainer']
    message = f'Latest {name} (`{device}`) [OrangeFox](https://wiki.orangefox.tech/en/home) Builds:\n' \
              f'_Maintainer:_ {maintainer}\n'
    stable = info['stable_build']
    stable_markup = InlineKeyboardButton(f"{stable}", f"{url}-Stable/{device}/{stable}")
    beta_markup = None
    try:
        beta = info['beta_build']
        beta_markup = InlineKeyboardButton(f"{beta}", f"{url}-Beta/{device}/{beta}")
        has_beta = True
    except KeyError:
        pass
    if has_beta:
        keyboard = [[stable_markup], [beta_markup]]
    else:
        keyboard = [[stable_markup]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    status = True
    return message, status, reply_markup