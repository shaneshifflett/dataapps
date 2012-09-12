from datetime import datetime, timedelta
import re, unicodedata

from django.conf import settings
from django.core.paginator import Paginator, InvalidPage, EmptyPage

def date_range(start_date=None, end_date=None):
    if start_date and end_date:
        one_day = timedelta(days=1)
        date_list = []
        # Only taking date into account, and not the specific time
        current_date = datetime(year=start_date.year,month=start_date.month,day=start_date.day)
        while current_date <= end_date:
            date_list.append(current_date)
            current_date = current_date + one_day
        return date_list
    return None

def is_secure(request):
        
        if not settings.PRODUCTION and ('8443' in request.get_host()):
            return True
        
        if request.is_secure():
            return True
        if request.META.get('SERVER_PORT', '8000') == '443':
            return True
        if 'HTTP_X_FORWARDED_SSL' in request.META:
            return request.META['HTTP_X_FORWARDED_SSL'] == 'on'
        
        return False
    
def paginate_list(request, obj_list, limit=5):
    pages = Paginator(obj_list, limit)
    
    try:
        page = int(request.GET.get('page', '1'))
    except:
        page = 1
        
    try:
        current_page = pages.page(page)
    except (EmptyPage, InvalidPage):
        current_page = pages.page(pages.num_pages)

    return pages, current_page

def slugify(title, id=None, unique_against_klass=None):
    if type(title) == str:
        title = unicode(title)
    title = unicodedata.normalize('NFKD', title).encode('ascii', 'ignore')
    title = unicode(re.sub('[^\w\s-]', '', title).strip().lower())
    maxchars = 40
    removelist = ["a", "an", "as", "at", "before", "but", "by", "for", "from",
                  "is", "in", "into", "like", "of", "off", "on", "onto", "per",
                  "since", "than", "the", "this", "that", "to", "up", "via",
                  "with", "i", "or"]
    title = title.replace('-', ' ')
    words = title.split(' ')
    slug_words = []
    c = 0
    for word in words:
        word = word.strip()
        if not word or word in removelist:continue
        if c > 0: word = u"-%s" %word
        if c + len(word) > maxchars: continue
        c += len(word)
        slug_words.append(word)
    if not id and not unique_against_klass:
        return "".join(slug_words)
    else:
        i = 0
        while True:
            slug = "".join(slug_words)+"-%s" %i if i else "".join(slug_words)
            found = unique_against_klass.objects.filter(slug=slug)
            if id:
                found = found.exclude(id=id)
            if not found:
                return slug
            i += 1
            slug = "".join(slug_words)+"-%s" %i
            if len(slug) > maxchars:
                slug_words.pop()

def avg(values):
    return float(sum(values))/len(values)

def median(values):
    """This will always return a float, for the sake of consistency.
    """
    vals = sorted(values)
    mid = len(vals)/2

    if len(vals) % 2:
        return float(vals[mid])
    else:
        return avg(vals[mid-1:mid+1])