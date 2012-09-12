import re, urllib2

import BeautifulSoup

from bike_accidents.models import BikeAccident, ViolationCode
from generics.cleaner import CleanHtml

base_url = 'http://www.dmv.ca.gov/pubs/vctop/d11/vc%s.htm'


def run():
    not_found = []
    codes = []
    scraped = {}
    
    for row in BikeAccident.objects.all():
        codes.append(row.violation_code)
    
    codes = set(codes)
    print "there are %s codes" %len(codes)
    for code in codes:
        if not code: continue
        original_code = code
        if '.1' in code:
            code = code.replace('.1', '')
        #print row.violation_code
        url = base_url %code
        #print url
        try:
            f = urllib2.urlopen(url)
            code_used = code
            print "found %s on first try" %url
            #print f.read()
            #break
        except urllib2.HTTPError:
            try:
                print "nothing found for %s, trying without letters" %code
                again = base_url %re.sub("[^0-9]", "", code)
                if url != again:
                    f = urllib2.urlopen(again)
                    code_used = re.sub("[^0-9]", "", code)
                    print "found %s on second try" %again
                else:
                    print "really nothing found for %s" %url
                    not_found.append(url)
                    continue
            except urllib2.HTTPError:
                print "last nothing found for %s" %url
                not_found.append(url)
                continue
        title, body = parseout(f.read())
        body = body.replace(code_used+'.', '')
        body = body.replace('&nbsp;', '')
        if not title:
            title = original_code
        
        scraped[original_code] = {'title': title, 'body': body}
        v, created = ViolationCode.objects.get_or_create(code=original_code, defaults={'body': body, 'title': title, })
        if not created:
            v.body = body
            v.title = title
            v.save()
        #print code+'.'
        #print body
        #break
    
    print "didnt find %s records" %len(not_found)
    print not_found
    print scraped
    

def parseout(html):
    soup = BeautifulSoup.BeautifulSoup(html)
    content = soup.findAll('div', attrs={'id': 'app_content'})
    if not content: return None
    content = content[0]
    ptags = []
    for p in content.findAll('p'):
        ptags.append("%s" %p)
    
    contents = "\n".join(ptags)
    title = content.findAll('h4')
    if title:
        title = title[0].text
    else:
        title = None
    body = CleanHtml(value=contents, tags_allowed=['p',]).clean()
    return (title, body)
    #print "I parsed out:"
    #print "Title: %s" %title
    #print "Body: %s" %body