from django import template
from django.conf import settings
from django.core.paginator import InvalidPage, EmptyPage
from django.db.models import Q

register = template.Library()

@register.inclusion_tag('generics/paginate_data.html', takes_context=True)
def paginate_data(context, pages):
    request = context['request']
    try:
        page = int(request.GET.get('page', '1'))
    except:
        page = 1
        
    try:
        current_page = pages.page(page)
    except (EmptyPage, InvalidPage):
        current_page = pages.page(pages.num_pages)
    
    if pages.num_pages <= 9:
        context['start_list'] = range(1, (pages.num_pages+1))
    else:
        if page >= (pages.num_pages-5):
            context['start_list'] = range(1, 4)
            context['end_list'] = range(pages.num_pages-4, pages.num_pages+1)
        else:
            if page > 5:
                context['start_list'] = range(page-4, page+1)
            else:
                context['start_list'] = range(1, 6)
            context['end_list'] = range(pages.num_pages-2, pages.num_pages+1)
 
    q = ['sort', 'date_from', 'date_to', 'accident_type', 'at_fault', 'violation'\
        , 'lighting', 'county', 'road_condition', 'street1', 'street2']
    add = []
    inputs = {}
    for key in q:
        if request.GET.get(key):
            add.append('%s=%s' %(key, request.GET[key]))
            inputs[key] = request.GET[key]
    if add:
        context['qs'] = "&".join(add)
        context['inputs'] = inputs
    
    context['pages'] = pages
    context['current_page'] = current_page
    context['current_page_num'] = page
    context['show_pages'] = pages.num_pages > 1
    return context

@register.inclusion_tag('generics/paginate.html', takes_context=True)
def paginate(context, pages):
    request = context['request']
    try:
        page = int(request.GET.get('page', '1'))
    except:
        page = 1
        
    try:
        current_page = pages.page(page)
    except (EmptyPage, InvalidPage):
        current_page = pages.page(pages.num_pages)
    
    if pages.num_pages <= 9:
        context['start_list'] = range(1, (pages.num_pages+1))
    else:
        if page >= (pages.num_pages-5):
            context['start_list'] = range(1, 4)
            context['end_list'] = range(pages.num_pages-4, pages.num_pages+1)
        else:
            if page > 5:
                context['start_list'] = range(page-4, page+1)
            else:
                context['start_list'] = range(1, 6)
            context['end_list'] = range(pages.num_pages-2, pages.num_pages+1)
            
    
    context['pages'] = pages
    context['current_page'] = current_page
    context['current_page_num'] = page
    context['show_pages'] = pages.num_pages > 1
    return context