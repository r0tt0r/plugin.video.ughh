#UGHH - by r0tt 2012. V0.0.3

import urllib,urllib2,re,string,xbmcaddon,xbmcplugin,xbmcgui,socket,sys,os

if sys.version_info < (2, 7):
    import json as simplejson
else:
    import simplejson

timeout = 25
socket.setdefaulttimeout(timeout)
pluginhandle = int(sys.argv[1])

try:
    import StorageServer
except:
    import storageserverdummy as StorageServer
 
cache = StorageServer.StorageServer("ArtworkDownloader",24)
addon = xbmcaddon.Addon('plugin.video.ughh')
scriptpath = addon.getAddonInfo('path')
base='http://www.undergroundhiphop.com/video/index.asp?'
q = scriptpath+'/icon.png'

def CATEGORIES():
        addDir('New Videos',base + 'Category=All&Sort=Newest&InHD=All&Null=1&Page=',1,q)
        addDir('New Top Rated',base + 'Category=All&Sort=TopRated&InHD=All&Null=1&Page=',1,q)
        addDir('Old School',base + 'Category=MusicVideo_OS&Page=',1,q)
        addDir('Old Top Rated',base + 'Category=MusicVideo_OS&Null=Newest&InHD=All&Null=1&Sort=TopRated&Page=',1,q)
        addDir('Search','&keywords=',1,q)
        addDir('#',base + 'Category=MusicVideo&Sort=Newest&InHD=All&Null=5&PageLetter=%23&Page=',1,q)
        url = base + 'Category=MusicVideo&Sort=Newest&InHD=All&Null=5&PageLetter='
        p = '&Page='
        array = string.uppercase[:26]
        for char in array:
            addDir(char,url + str(char) + p,1,q)
        xbmcplugin.endOfDirectory(pluginhandle)
        
def INDEX(url):
        if url == '&keywords=':
            search = Search()
            url=base + 'searchby=All&searchTarget=video' + url + search    
        req=urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64; rv:17.0) Gecko/17.0 Firefox/17.0')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        page12=re.compile('valign=\"bottom\" class=\"s\"><nobr>Page <b>(.+?)<\/b> of <b>(.+?)<\/b> \(<b>').findall(link)
        page12=str(page12).strip('[(\')]')
        page1=re.compile("(\d{1,2})', '").findall(str(page12))
        page2=re.compile("', '(\d{1,2})").findall(str(page12))
        if not page1==page2:
            page1=int(str(page1).strip("['']"))+1
            url=re.sub("&Page=([0-9]*)", "&Page=", url)
            pageurl=url + str(page1).strip("['']")
            addDir("Go To Page " + str(page1) + ' of ' + str(page2).strip("['']"), pageurl, 1, "")
        else:
            page1=int(str(page1).strip("['']"))-1
            if not page1==0:
                url=re.sub("&Page=([0-9]*)", "&Page=", url)            
                pageurl=url + str(page1).strip("['']")
                addDir("Go To Page " + str(page1) + ' of ' + str(page2).strip("['']"), pageurl, 1, "")
        title=re.compile('http://ughh.com/video/images/snapshots/(.+?_.+?).jpg').findall(link)
        video1=re.compile('<td align=\'center\' class=\'w3\'><a href=\'(/video/detail.asp\?t=.+?)\' class=\"HoverLink\">').findall(link)
        video=['http://www.undergroundhiphop.com'+li for li in video1]
        thumb=re.compile('(http://ughh.com/video/images/snapshots/.+?.jpg)').findall(link)
        match=zip(title, video, thumb)
        for name,url,thumb in match:
                name = name.replace("_"," - ")
                name = re.sub(r"(?<=\w)([A-Z])", r" \1", name)
                addDir(name,url,2,thumb)
        xbmcplugin.endOfDirectory(pluginhandle)

def VIDEOLINKS(url,name):
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64; rv:17.0) Gecko/17.0 Firefox/17.0')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        match=re.compile('flashvars=\"videoPath=(http://www.undergroundhiphop.com/video/view.asp\?ID=.+?)&').findall(link)
        match1 = str(match)
        match1 = match1.strip("'[]'")
        track = str(name) + '.mp4'
        for url in match:
                action = ''
                dialog = xbmcgui.Dialog()
                action = dialog.yesno("Download or Play", "", "                                              Choose", "", "Play", "Download")
                if ( action == 1 ):
                    DownloaderClass(str(match1),track)
                    dialog.ok("Download Completed", "", "                   File has been downloaded to home folder")
                else:
                    addLink(name,url,'')
        xbmcplugin.endOfDirectory(pluginhandle)

def DL(match1,track):
    DownloaderClass(str(match1),track)
    xbmcplugin.endOfDirectory(pluginhandle)

def DownloaderClass(url,dest):
    dialog = xbmcgui.DialogProgress()
    dialog.create("UGHH Video DL","Downloading File",url)
    urllib.urlretrieve(url,dest,lambda nb, bs, fs, url=url: _pbhook(nb,bs,fs,url,dialog))

def _pbhook(numblocks, blocksize, filesize, url=None,dialog=None):
    try:
        percent = min((numblocks*blocksize*100)/filesize, 100)
        print percent
        dialog.update(percent)
    except:
        percent = 100
        dialog.update(percent)
    if dialog.iscanceled(): 
        print "DOWNLOAD CANCELLED"
        dialog.close()
    if percent == 100:
        dialog.close()
        xbmcplugin.endOfDirectory(pluginhandle)

def Search():
	search = ''
	keyboard = xbmc.Keyboard(search, '')
	keyboard.doModal()
	if (keyboard.isConfirmed()==False):
	  return
	search=keyboard.getText()
	search=str(search).replace(' ','+')
	if len(search) == 0:
	  return
	else:
	  return search

def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
                params=sys.argv[2]
                cleanedparams=params.replace('?','')
                if (params[len(params)-1]=='/'):
                        params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&')
                param={}
                for i in range(len(pairsofparams)):
                        splitparams={}
                        splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2:
                                param[splitparams[0]]=splitparams[1]
                                
        return param

def addLink(name,url,iconimage):
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
        return ok

def addDir(name,url,mode,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok
                  
params=get_params()
url=None
name=None
mode=None

try:
        url=urllib.unquote_plus(params["url"])
except:
        pass
try:
        name=urllib.unquote_plus(params["name"])
except:
        pass
try:
        mode=int(params["mode"])
except:
        pass

print "Mode: "+str(mode)
print "URL: "+str(url)
print "Name: "+str(name)

if mode==None or url==None or len(url)<1:
        print ""
        CATEGORIES()
       
elif mode==1:
        print ""+url
        INDEX(url)
        
elif mode==2:
        print ""+url
        VIDEOLINKS(url,name)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
