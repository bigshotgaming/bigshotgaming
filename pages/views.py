from django.shortcuts import render_to_response
from django.core.exceptions import ObjectDoesNotExist
from django.template import RequestContext
from django.contrib.syndication.views import Feed
from djangobb_forum.models import Category

def index(request):
    try:
        posts = Category.objects.get(name='News').forums.get(name='News').topics.select_related().order_by('-created')[:3]
    except ObjectDoesNotExist:
        posts = None
    return render_to_response('index.html', {'news_posts':posts}, context_instance=RequestContext(request))
    
class NewsFeed(Feed):
    title = "Big Shot Gaming News Feed"
    description = "News from your friends at Big Shot Gaming"
    link = '/rss/'
    
    def items(self):
        posts = Category.objects.get(name='News').forums.get(name='News').topics.select_related().order_by('-created')[:3]
        return posts
        
    def item_title(self, item):
        return item.name
        
    def item_description(self, item):
        return item.posts.all()[0].body_html
        
    def item_link(self, item):
        return item.get_absolute_url()
        
    def item_author_name(self, item):
        return item.posts.all()[0].user.username
        
    def item_pubdate(self, item):
        return item.posts.all()[0].updated or item.posts.all()[0].created