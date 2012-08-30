import datetime
from django.shortcuts import render_to_response
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.template import RequestContext
from django.contrib.syndication.views import Feed
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from pages.forms import ContactForm
from sponsorship.models import Sponsor
from events.models import Event
from pages.models import Post


#TODO: Possibly switch these to a generic view in the future, if we decide that's the right way to go.
# def index(request):
#     try:
#         posts = Category.objects.get(name='News').forums.get(name='News').topics.select_related().order_by('-created')[:3]
#     except ObjectDoesNotExist:
#         posts = None
#     return render_to_response('index.html', {'news_posts':posts}, context_instance=RequestContext(request))
def index(request):
    posts_list = Post.objects.filter(category__exact='N').order_by("-created_time")
    paginator = Paginator(posts_list, 5)

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        posts = paginator.page(page)
    except (EmptyPage, InvalidPage):
        posts = paginator.page(paginator.num_pages)
    # try: 
    #     posts = paginator.page(page)
    # except PageNotAnInteger:
    #     posts = paginator.page(1)
    # except EmptyPage:
    #     posts = paginator.page(paginator.num_pages)
    return render_to_response("index.html", {'posts':posts}, context_instance=RequestContext(request))

def reviews(request):
    posts_list = Post.objects.filter(category__exact='R').order_by("-created_time")
    paginator = Paginator(posts_list, 5)

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        posts = paginator.page(page)
    except (EmptyPage, InvalidPage):
        posts = paginator.page(paginator.num_pages)
    # try: 
    #     posts = paginator.page(page)
    # except PageNotAnInteger:
    #     posts = paginator.page(1)
    # except EmptyPage:
    #     posts = paginator.page(paginator.num_pages)
    return render_to_response("index.html", {'posts':posts}, context_instance=RequestContext(request))

def post(request, pk):
    post = Post.objects.get(pk=int(pk))
    return render_to_response('post.html', {'post':post}, context_instance=RequestContext(request))

def sponsors(request):
    ''' 
    This is how we determine who's been sponsoring us lately.
    If no events are currently active, we grab the most recent event.
    No more than one event can be active concurrently at this time.
    '''
    try:
        # thanks to avidal for the below
        event = Event.objects.filter(Q(is_active=True) | Q(end_date__lte=datetime.datetime.now())).order_by('-is_active', '-end_date')[0]
    except IndexError:
        # we do this so that if no events are returned, the below code does not throw an exception
        event = None
    sponsors = Sponsor.objects.filter(event=event, eventsponsor__status__in=['p', 'c', 'r', 'f']).exclude(banner='')
    return render_to_response('sponsors.html', {'sponsors':sponsors}, context_instance=RequestContext(request))

@login_required
def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            staff_member = form.cleaned_data['staff_member']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            sender = (request.user.email)
            recipients = [staff_member.email, sender]

            from django.core.mail import send_mail
            send_mail(subject, message, sender, recipients)
            return HttpResponseRedirect('/thanks/')
    else:
        form = ContactForm() # An unbound form
    return render_to_response('contact.html', {'form': form}, context_instance=RequestContext(request))

    
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
