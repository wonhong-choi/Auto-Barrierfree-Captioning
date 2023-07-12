from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from users.models import Post

from .models import Reply
from .forms import ReplyForm

# Create your views here.
@login_required
def create(request, post_id):
    if request.method == "POST":
        replyForm = ReplyForm(request.POST)
        if replyForm.is_valid():
            reply = replyForm.save(commit=False)
            reply.author = request.user
            print(request.user)
            post = Post()
            post.id = post_id
            reply.post = post
            reply.save()
    return redirect('/blog/'+str(post_id))

@login_required
def delete(request, post_id, com_id):
    my_com = Reply.objects.get(id=com_id)
    my_com.delete()
    return redirect('/blog/'+str(post_id))

@login_required
def edit(request, post_id, com_id):
    post = Post.objects.prefetch_related('reply_set').get(id=post_id)
    comment = get_object_or_404(Reply, id=com_id)
    if request.method == "POST":
        replyForm = ReplyForm(request.POST, instance=comment)
        if replyForm.is_valid():
            comment = replyForm.save()
            return redirect('user:blogdt', post_id)
    else:
        replyForm = ReplyForm(instance=comment)
    return render(request, 'comment_edit.html', {'post':post, 'comment':comment})
