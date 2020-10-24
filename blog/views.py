from django.shortcuts import render,get_object_or_404
from .models import Post,Comment
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage 
from django.views.generic import ListView
from .forms import EmailPostForm,CommentForm 
from django.core.mail import send_mail

def post_list(request):
    object_list = Post.published.all()
    paginator=Paginator(object_list,3) # 3 posts in each page
    page=request.GET.get('page')
    try:
        posts=paginator.page(page)
    except PageNotAnInteger:
        #if page is not an integer deliver the first page
        posts =paginator.page(1)
    except EmptyPage:
        # if page is out of range deliver the last page
        posts = paginator.page(paginator.num_pages)
    return render(request,
            'blog/post/list.html',
            {'page':page,
                'posts':posts
                }
            )

def post_detail(request,year,month,day,post):
    post=get_object_or_404(Post,slug=post,
            status='published',
            publish__year=year,
            publish__month=month,
            publish__day=day)

    comments = post.comments.filter(active=True)

    new_comment = None 

    if request.method == 'POST':

        comment_form = CommentForm(data =request.POST)

        if comment_form.is_valid():
            new_comment = comment.form.save(commit=False)
            new_comment.post =post 
            new_comment.save()

    else:
        comment_form=CommentForm()

    return render(request,
            'blog/post/detail.html',
            {'post':post,
                'comments':comments,
                'new_comment': new_comment,
                'comment_form':comment_form 

                })

class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name='posts'
    paginate_by = 3
    template_name ='blog/post/list.html'

def post_share(request,post_id):
    post=get_object_or_404(Post,id=post_id,status='published')
    sent=False
    if request.method == 'POST':
        form= EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data 
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = '{}({}) recommends you reading "{}"'.format(cd['name'],cd['email'],post.title)
            message = 'Read "{}" at {}\n\n{}\'scomments:{}'.format(post.title,post_url,cd['name'],cd['comments'])
            send_mail(subject,message,'admin@myblog.com',[cd['to']])
            sent=True 
    else:
        form = EmailPostForm()
    return render(request,'blog/post/share.html',{'post':post,'form':form,'sent':sent})




