# -*- coding: utf-8 -*-
import routing
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import re
from bs4 import BeautifulSoup
import requests
import inputstreamhelper
import json
import pickle
import os

_addon = xbmcaddon.Addon()
_profile = xbmc.translatePath( _addon.getAddonInfo('profile'))
plugin = routing.Plugin()

_baseurl = 'https://voyo.markiza.sk/'
_loginCheckUrl = 'https://crm.cms.markiza.sk/api/v1/users/login-check'
_loginUrl = 'https://voyo.markiza.sk/prihlasenie'
_loginFormDoValue = 'content204-loginForm-form-submit'
_tvShowsUrl = 'api/v1/shows/genres?category=voyo-4&sort=title__asc&limit=64&page=1'
_moviesUrl = 'api/v1/shows/genres?category=voyo-5&sort=title__asc&limit=64&page=1'
_seriesUrl = 'api/v1/shows/genres?category=voyo-3&sort=title__asc&limit=64&page=1'
_kidsUrl = 'api/v1/shows/genres?category=voyo-7&sort=title__asc&limit=64&page=1'
_wholeEpisodesUrl = '/cele-diely'

@plugin.route('/list_shows_next')
def list_shows_next():
    return list_shows(0)

@plugin.route('/list_shows/<type>')
def list_shows(type):
    xbmcplugin.setContent(plugin.handle, 'tvshows')
    try:
        url = plugin.args['show_url'][0]
    except KeyError:
        url = _baseurl+_tvShowsUrl
    soup = get_page(url)
    listing = []
    articles = soup.find_all('div', {'class': 'c-video-box'})
    for article in articles:
        title = article.h3.a.contents[0].encode('utf-8')
        list_item = xbmcgui.ListItem(label=title)
        list_item.setInfo('video', {'mediatype': 'tvshow', 'title': title})
        list_item.setArt({'poster': article.div.img['data-src']})
        listing.append((plugin.url_for(get_list, category = False, show_url = article.h3.a['href'], showtitle = title), list_item, True))
    next = soup.find('div', {'class': 'load-more'})
    if next:
        list_item = xbmcgui.ListItem(label=_addon.getLocalizedString(30004))
        listing.append((plugin.url_for(list_shows_next, show_url = next.find('button')['data-href']), list_item, True))

    xbmcplugin.addDirectoryItems(plugin.handle, listing, len(listing))
    xbmcplugin.endOfDirectory(plugin.handle)

@plugin.route('/list_movies_next')
def list_movies_next():
    return list_movies(0)

@plugin.route('/list_movies/<type>')	
def list_movies(type):
    xbmcplugin.setContent(plugin.handle, 'tvshows')
    try:
        url = plugin.args['show_url'][0]
    except KeyError:
        url = _baseurl+_moviesUrl
    soup = get_page(url)
    listing = []
    articles = soup.find_all('div', {'class': 'c-video-box'})
    for article in articles:
        title = article.h3.a.contents[0].encode('utf-8')
        list_item = xbmcgui.ListItem(label=title)
        list_item.setInfo('video', {'mediatype': 'movie', 'title': title})
        list_item.setArt({'poster': article.div.img['data-src']})
        list_item.setProperty('IsPlayable', 'true')
        listing.append((plugin.url_for(get_video, article.h3.a['href']), list_item, False))
    next = soup.find('div', {'class': 'load-more'})
    if next:
        list_item = xbmcgui.ListItem(label=_addon.getLocalizedString(30004))
        listing.append((plugin.url_for(list_movies_next, show_url = next.find('button')['data-href']), list_item, True))

    xbmcplugin.addDirectoryItems(plugin.handle, listing, len(listing))
    xbmcplugin.endOfDirectory(plugin.handle)

@plugin.route('/list_serials_next')
def list_serials_next():
    return list_serials(0)

@plugin.route('/list_serials/<type>')
def list_serials(type):
    xbmcplugin.setContent(plugin.handle, 'tvshows')
    try:
        url = plugin.args['show_url'][0]
    except KeyError:
        url = _baseurl+_seriesUrl
    soup = get_page(url)
    listing = []
    articles = soup.find_all('div', {'class': 'c-video-box'})
    for article in articles:
        title = article.h3.a.contents[0].encode('utf-8')
        list_item = xbmcgui.ListItem(label=title)
        list_item.setInfo('video', {'mediatype': 'tvshow', 'title': title})
        list_item.setArt({'poster': article.div.img['data-src']})
        listing.append((plugin.url_for(get_list, category = False, show_url = article.h3.a['href'], showtitle = title), list_item, True))
    next = soup.find('div', {'class': 'load-more'})
    if next:
        list_item = xbmcgui.ListItem(label=_addon.getLocalizedString(30004))
        listing.append((plugin.url_for(list_serials_next, show_url = next.find('button')['data-href']), list_item, True))

    xbmcplugin.addDirectoryItems(plugin.handle, listing, len(listing))
    xbmcplugin.endOfDirectory(plugin.handle)

@plugin.route('/list_kids_next')
def list_kids_next():
    return list_kids(0)

@plugin.route('/list_kids/<type>')
def list_kids(type):
    xbmcplugin.setContent(plugin.handle, 'tvshows')
    try:
        url = plugin.args['show_url'][0]
    except KeyError:
        url = _baseurl+_kidsUrl
    soup = get_page(url)
    listing = []
    articles = soup.find_all('div', {'class': 'c-video-box'})
    for article in articles:
        title = article.h3.a.contents[0].encode('utf-8')
        showUrl = article.h3.a['href']
        list_item = xbmcgui.ListItem(label=title)
        list_item.setArt({'poster': article.div.img['data-src']})
        if not "/film" in showUrl:
            list_item.setInfo('video', {'mediatype': 'tvshow', 'title': title})
            listing.append((plugin.url_for(get_list, category = False, show_url = showUrl, showtitle = title), list_item, True))
        else:
            list_item.setInfo('video', {'mediatype': 'movie', 'title': title})
            list_item.setProperty('IsPlayable', 'true')
            listing.append((plugin.url_for(get_video, showUrl), list_item, False))
    next = soup.find('div', {'class': 'load-more'})
    if next:
        list_item = xbmcgui.ListItem(label=_addon.getLocalizedString(30004))
        listing.append((plugin.url_for(list_kids_next, show_url = next.find('button')['data-href']), list_item, True))

    xbmcplugin.addDirectoryItems(plugin.handle, listing, len(listing))
    xbmcplugin.endOfDirectory(plugin.handle)

@plugin.route('/list_recent/')
def list_recent():
    xbmcplugin.setContent(plugin.handle, 'episodes')
    soup = get_page(_baseurl)
    listing = []
    articles = soup.find('section', {'class':'b-main-section b-section-articles my-5'}).find_all('article', {'class':'b-article b-article-no-labels'})
    for article in articles:
        menuitems = []
        title = article.find('span', {'class':'e-text'}).get_text()
        dur = article.find('span', {'class':'e-duration'})
        show_url = re.compile('(.+)\/.+\/').findall(article.find('a')['href'])[0]
        menuitems.append(( _addon.getLocalizedString(30005), 'XBMC.Container.Update('+plugin.url_for(get_list, category = False, show_url = show_url)+')' ))
        if dur:
            dur = get_duration(article.find('span', {'class':'e-duration'}).get_text())
        list_item = xbmcgui.ListItem(label = title)
        list_item.setInfo('video', {'mediatype': 'episode', 'title': title, 'duration': dur})
        list_item.setArt({'icon': article.find('img', {'class':'e-image'})['data-original']})
        list_item.setProperty('IsPlayable', 'true')
        list_item.addContextMenuItems(menuitems)
        listing.append((plugin.url_for(get_video, article.find('a')['href']), list_item, False))

    xbmcplugin.addDirectoryItems(plugin.handle, listing, len(listing))
    xbmcplugin.endOfDirectory(plugin.handle)

@plugin.route('/get_list/')
def get_list():
    xbmcplugin.setContent(plugin.handle, 'episodes')
    listing = []  
    url = plugin.args['show_url'][0]
    category = plugin.args['category'][0]
    if category == 'False':
        list_item = xbmcgui.ListItem(label=_addon.getLocalizedString(30007))
        listing.append((plugin.url_for(get_category, show_url = url, showtitle = plugin.args['showtitle'][0]), list_item, True))
        #url = plugin.args['show_url'][0]+_wholeEpisodesUrl
    soup = get_page(url)
    if 'showtitle' in plugin.args:
        showtitle = plugin.args['showtitle'][0].encode('utf-8')
    else:
        showtitle = soup.find('h1', 'title').get_text().encode('utf-8')
    articles = soup.find_all('article', 'c-video-box -media')
    count = 0
    for article in articles:
        title = article.h3.a.contents[0]
        dur = article.find('span', {'class':'e-duration'})
        if dur:
        	dur = get_duration(dur.get_text())
        list_item = xbmcgui.ListItem(title)
        list_item.setInfo('video', {'mediatype': 'episode', 'tvshowtitle': showtitle, 'title': title, 'duration': dur})
        list_item.setArt({'thumb': article.img['data-src']})
        list_item.setProperty('IsPlayable', 'true')
        listing.append((plugin.url_for(get_video, article.h3.a['href']), list_item, False))
        count +=1
    next = soup.find('div', {'class': 'load-more'})
    if next:
        list_item = xbmcgui.ListItem(label=_addon.getLocalizedString(30004))
        listing.append((plugin.url_for(get_list, category = category, show_url = next.find('button')['data-href'], showtitle = showtitle), list_item, True))

    xbmcplugin.addDirectoryItems(plugin.handle, listing, len(listing))
    xbmcplugin.endOfDirectory(plugin.handle)

@plugin.route('/get_category/')
def get_category():
    listing = []
    soup = get_page(plugin.args['show_url'][0])
    navs = soup.find('div', {'class': 'c-video-category-wrapper'}).find('div', {'class': 'dropdown-menu'})
    if navs:
        for nav in navs.find_all('a'):
            list_item = xbmcgui.ListItem(nav.text)
            list_item.setInfo('video', {'mediatype': 'tvshow'})
            #list_item.setInfo('video', {'mediatype': 'episode'})
            listing.append((plugin.url_for(get_list, category = False, show_url = nav['data-url'], showtitle = plugin.args['showtitle'][0]), list_item, True))

    xbmcplugin.addDirectoryItems(plugin.handle, listing, len(listing))
    xbmcplugin.endOfDirectory(plugin.handle)

@plugin.route('/get_video/<path:url>')
def get_video(url):
    PROTOCOL = 'mpd'
    DRM = 'com.widevine.alpha'
    source_type = _addon.getSetting('source_type')
    soup = get_page(url)
    desc = soup.find('meta', {'name':'description'})['content'].encode('utf-8')
    try:
        showtitle = soup.find('h2', {'class':'subtitle'}).find('a').get_text().encode('utf-8')
    except AttributeError:
                showtitle = None
    title = soup.find('h1', {'class':'title'}).get_text().encode('utf-8')
    embeded = get_page(soup.find('div', {'class':'c-player-wrap'}).find('iframe')['src']).find_all('script')[-1]
    json_data = json.loads(re.compile('{\"tracks\":(.+?),\"duration\"').findall(str(embeded))[0])

    if json_data:
        print (json_data)
        stream_data = json_data[source_type][0]
        list_item = xbmcgui.ListItem()
        list_item.setInfo('video', {'mediatype': 'episode', 'tvshowtitle': showtitle, 'title': title, 'plot' : desc})
        if not 'drm' in stream_data and source_type == 'HLS':
            list_item.setPath(stream_data['src'])
        else:
            is_helper = inputstreamhelper.Helper(PROTOCOL, drm=DRM)
            if is_helper.check_inputstream():
                stream_data = json_data['DASH'][0]
                print(stream_data['type'])
                list_item.setPath(stream_data['src'])
                list_item.setContentLookup(False)
                list_item.setMimeType('application/xml+dash')
                list_item.setProperty('inputstream', 'inputstream.adaptive')
                list_item.setProperty('inputstream.adaptive.manifest_type', PROTOCOL)
                if 'drm' in stream_data:
                    drm = stream_data['drm'][1]
                    list_item.setProperty('inputstream.adaptive.license_type', DRM)
                    list_item.setProperty('inputstream.adaptive.license_key', drm['serverURL'] + '|' + 'X-AxDRM-Message=' + drm['headers'][0]['value'] + '|R{SSM}|')
        xbmcplugin.setResolvedUrl(plugin.handle, True, list_item)
    else:
        xbmcgui.Dialog().notification(_addon.getAddonInfo('name'),_addon.getLocalizedString(30006), xbmcgui.NOTIFICATION_ERROR, 5000)


def get_duration(dur):
    duration = 0
    l = dur.strip().split(':')
    for pos, value in enumerate(l[::-1]):
        duration += int(value) * 60 ** pos
    return duration

def get_page(url):
	s = get_session()
	r = s.get(url, headers={'User-Agent': 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:80.0) Gecko/20100101 Firefox/80.0'})
	return BeautifulSoup(r.content, 'html.parser')

def get_session():
	s = requests.session()
	# Load cookies and test auth
	cookie_file = _profile+"cookie"
	cookie_file_exists = os.path.isfile(cookie_file)
	if cookie_file_exists:
		with open(cookie_file, 'rb') as f:
			s.cookies.update(pickle.load(f))
		auth = test_auth(s)
		if auth == 0:
			try:
				os.remove(cookie_file)
			except:
				print ("File not found.")
	else:
		s = make_login(s)
	return s
	
def test_auth(s):
	r = s.get(_loginCheckUrl, headers={'User-Agent': 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:80.0) Gecko/20100101 Firefox/80.0'})
	try:
		if r.json()['data']['logged_in'] == True:
			auth = 1
	except KeyError:
		auth = 0
	return auth

def make_login(s):
	cookie_file = _profile+"cookie"
	username = xbmcplugin.getSetting(plugin.handle, 'username')
	password = xbmcplugin.getSetting(plugin.handle, 'password')
	data = {
		'email': username,
		'password': password,
		'_do': _loginFormDoValue
	}
	r = s.post(_loginUrl, headers={'User-Agent': 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:80.0) Gecko/20100101 Firefox/80.0'}, data=data)
	with open(cookie_file, 'wb') as f:
		pickle.dump(s.cookies, f)
	return s

def performCredentialCheck():
	username = xbmcplugin.getSetting(plugin.handle, 'username')
	password = xbmcplugin.getSetting(plugin.handle, 'password')

	if not username or not password:
		registration_notice = xbmcgui.Dialog()
		registration_notice.ok('VOYO účet', 'Pro přehrávání pořadů je potřeba účet s aktivním předplatným na voyo.nova.cz\n\nPokud účet ještě nemáte, zaregistrujte se na voyo.nova.cz, předplaťte účet na měsíc nebo rok a v dalším okně vyplňte přihlašovací údaje.')

		username_prompt = xbmcgui.Dialog()
		usr = username_prompt.input('Uživatel (e-mail)')

		if not usr:
			return False
		_addon.setSetting(id='username', value=usr)

		password_prompt = xbmcgui.Dialog()
		pswd = password_prompt.input('Heslo', option=xbmcgui.ALPHANUM_HIDE_INPUT)

		if not pswd:
			return False
		_addon.setSetting(id='password', value=pswd)

	return True
	
@plugin.route('/')
def root():

	try:
		os.mkdir(_profile)
	except OSError:
		print ("Folder already exists.")
    
	listing = []
	list_item = xbmcgui.ListItem('Pořady')
	list_item.setArt({'icon': 'DefaultTVShows.png'})
	listing.append((plugin.url_for(list_shows, 0), list_item, True))
	
	list_item = xbmcgui.ListItem('Seriály')
	list_item.setArt({'icon': 'DefaultTVShows.png'})
	listing.append((plugin.url_for(list_serials, 0), list_item, True))
	
	list_item = xbmcgui.ListItem('Filmy')
	list_item.setArt({'icon': 'DefaultTVShows.png'})
	listing.append((plugin.url_for(list_movies, 0), list_item, True))	
	
	list_item = xbmcgui.ListItem('Pre deti')
	list_item.setArt({'icon': 'DefaultTVShows.png'})
	listing.append((plugin.url_for(list_kids, 0), list_item, True))	
	
	xbmcplugin.addDirectoryItems(plugin.handle, listing, len(listing))
	xbmcplugin.endOfDirectory(plugin.handle)

def run():
	credentialsAvailable = performCredentialCheck()

	if credentialsAvailable:
		plugin.run()
	else:
		xbmc.executebuiltin("Action(Back,%s)" % xbmcgui.getCurrentWindowId())
		sys.exit(1)
