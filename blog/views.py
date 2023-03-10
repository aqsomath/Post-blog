from django.core.mail import send_mail
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Count
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views import View

from taggit.models import Tag

from .forms import SharePostForm, CommentForm,SearchForm
from .models import Post, Comment

from django.contrib.postgres.search import SearchVector,SearchRank,SearchQuery,TrigramSimilarity


def post_list(request, tag_slug = None):
    form = SearchForm()
    query = None
    result = []
    object_list = Post.objects.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug = tag_slug)
        object_list = object_list.filter(tags__in = [tag])
    pagination = Paginator(object_list, 2)
    page_num = request.GET.get('page',1)
    posts = pagination.get_page(page_num)
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            result = Post.objects.annotate(
                search = SearchVector('title', 'body',),
            ).filter(search=query)


    return render(request,
                  'blog/post_list.html',
                  {'posts': posts,
                   'tag':tag,
                   'form':form,
                   'results':result,
                   'query':query}
                  )

def post_detail(request, id):
         post = Post.objects.get(id=id)
         form = CommentForm()
         comments = post.comments.all()
         if request.method == 'POST':
             form = CommentForm(request.POST)
             if form.is_valid():
                 Comment.objects.create(
                      post = post,
                      name = request.POST['name'],
                      body = request.POST['body'],
                      email = request.POST['email']

                 )
                 return redirect(reverse("blog:post_detail", kwargs={'id': post.id}))
         post_tags_ids = post.tags.values_list('id', flat=True)
         similar_posts = Post.objects.filter(tags__in = post_tags_ids).exclude(id=id)
         similar_posts = similar_posts.annotate(same_tags = Count('tags')).order_by('-same_tags', 'publish')

         return render(request,
                             'blog/post_detail.html',
                             {'post': post,
                              'form':form,
                              'comments':comments,
                              'similar_posts':similar_posts})

def post_delete(request, id):
    post = Post.objects.get(id=id)
    post.delete()
    return redirect('blog:post_list')



class PostShareView(View):
    def get(self,request):
       return render(request,'blog/post_share.html')
    def post(self, request):
        message = request.POST['message']
        name = request.POST['name']
        email = request.POST['email']
        send_mail(
            'Jamshid',
            message ,
            'settings.EMAIL_HOST_USER',
            [email],fail_silently=False
        )

        return render(request, 'blog/post_share.html')


def post_search(request):
    form = SearchForm()
    query = None
    result = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            result = Post.objects.annotate(
                similarity = TrigramSimilarity('title', query),
            ).filter(similarity__gt = 0.1
            ).order_by('-similarity')
    return render(request, 'blog/post_search.html', {"form":form, "query":query, "results":result})