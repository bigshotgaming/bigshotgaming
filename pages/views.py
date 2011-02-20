# Create your views here.
from django.shortcuts import render_to_response
from django.template import RequestContext
from djangobb_forum.models import Category

def index(request):
    posts = Category.objects.get(name='News').forums.get(name='News').topics.select_related().order_by('-created')[:3]
    return render_to_response('index.html', {'news_posts':posts}, context_instance=RequestContext(request))