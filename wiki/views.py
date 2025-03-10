import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template.loader import get_template
from django.conf import settings
from django.templatetags.static import static
from django.utils.html import escape
from django.core.files.storage import default_storage
from .models import Writeup, WriteupVersion
from .forms import UserUpdateForm
from django import forms
import markdown2
from taggit.models import Tag
from xhtml2pdf import pisa

# Form untuk Writeup
class WriteupForm(forms.ModelForm):
    class Meta:
        model = Writeup
        fields = ['title', 'content', 'is_public', 'tags']

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('writeup_list')
    else:
        form = UserCreationForm()
    return render(request, 'wiki/register.html', {'form': form})

@login_required
def writeup_list(request):
    writeups = Writeup.objects.filter(owner=request.user) | Writeup.objects.filter(is_public=True)
    tags = Tag.objects.all()
    tag_counts = {tag.name: Writeup.objects.filter(tags__name__in=[tag.name]).count() for tag in tags}
    return render(request, 'wiki/writeup_list.html', {'writeups': writeups, 'tags': tags, 'tag_counts': tag_counts})

@login_required
def writeup_detail(request, pk):
    writeup = get_object_or_404(Writeup, pk=pk)
    if not writeup.is_public and writeup.owner != request.user:
        return redirect('writeup_list')
    html_content = markdown2.markdown(writeup.content, extras=["fenced-code-blocks", "code-friendly"])
    return render(request, 'wiki/writeup_detail.html', {'writeup': writeup, 'html_content': html_content})

@login_required
def writeup_create(request):
    if request.method == 'POST':
        form = WriteupForm(request.POST)
        if form.is_valid():
            writeup = form.save(commit=False)
            writeup.owner = request.user
            writeup.save()
            form.save_m2m()  # Save tags
            return redirect('writeup_detail', pk=writeup.pk)
    else:
        form = WriteupForm()
    return render(request, 'wiki/writeup_form.html', {'form': form})

@login_required
def writeup_edit(request, pk):
    writeup = get_object_or_404(Writeup, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = WriteupForm(request.POST, instance=writeup)
        if form.is_valid():
            form.save()
            return redirect('writeup_detail', pk=writeup.pk)
    else:
        form = WriteupForm(instance=writeup)
    return render(request, 'wiki/writeup_form.html', {'form': form, 'edit': True})

@login_required
def toggle_visibility(request, pk):
    writeup = get_object_or_404(Writeup, pk=pk, owner=request.user)
    writeup.is_public = not writeup.is_public
    writeup.save()
    return redirect('writeup_detail', pk=pk)

@login_required
def rollback_writeup(request, pk, version_id):
    writeup = get_object_or_404(Writeup, pk=pk, owner=request.user)
    version = get_object_or_404(WriteupVersion, pk=version_id, writeup=writeup)
    writeup.title = version.title
    writeup.content = version.content
    writeup.save()
    return redirect('writeup_detail', pk=pk)

@login_required
def writeup_delete(request, pk):
    writeup = get_object_or_404(Writeup, pk=pk, owner=request.user)
    if request.method == 'POST':
        writeup.delete()
        return redirect('writeup_list')
    return render(request, 'wiki/writeup_confirm_delete.html', {'writeup': writeup})

@login_required
def search_writeups(request):
    query = request.GET.get('q')
    tag = request.GET.get('tag')
    writeups = Writeup.objects.filter(owner=request.user) | Writeup.objects.filter(is_public=True)
    
    if query:
        writeups = writeups.filter(title__icontains=query)
    if tag:
        writeups = writeups.filter(tags__name__in=[tag])
    
    tags = Tag.objects.all()
    tag_counts = {tag.name: Writeup.objects.filter(tags__name__in=[tag.name]).count() for tag in tags}
    return render(request, 'wiki/search_results.html', {'writeups': writeups, 'tags': tags, 'query': query, 'selected_tag': tag, 'tag_counts': tag_counts})

@login_required
def update_account(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        if user_form.is_valid():
            user_form.save()
            return redirect('update_account')
    else:
        user_form = UserUpdateForm(instance=request.user)
    return render(request, 'wiki/update_account.html', {'user_form': user_form})

@login_required
def change_password(request):
    if request.method == 'POST':
        password_form = PasswordChangeForm(user=request.user, data=request.POST)
        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)  # Important!
            return redirect('update_account')
    else:
        password_form = PasswordChangeForm(user=request.user)
    return render(request, 'wiki/change_password.html', {'password_form': password_form})

@login_required
def user_profile(request, username):
    user = get_object_or_404(User, username=username)
    writeups = Writeup.objects.filter(owner=user)
    return render(request, 'wiki/user_profile.html', {'profile_user': user, 'writeups': writeups})

@login_required
def export_writeup_pdf(request, pk):
    writeup = get_object_or_404(Writeup, pk=pk)
    if not writeup.is_public and writeup.owner != request.user:
        return redirect('writeup_list')
    
    template_path = 'wiki/writeup_pdf.html'
    context = {'writeup': writeup}
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{escape(writeup.title)}.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)
    
    # Handle static files
    def link_callback(uri, rel):
        if uri.startswith(settings.MEDIA_URL):
            path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ""))
        elif uri.startswith(settings.STATIC_URL):
            path = os.path.join(settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, ""))
        else:
            return uri
        if not os.path.isfile(path):
            raise Exception(f'Media URI must start with {settings.STATIC_URL} or {settings.MEDIA_URL}')
        return path

    pisa_status = pisa.CreatePDF(html, dest=response, link_callback=link_callback)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response