# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings
from .forms import (
    SingUpForm,
    ContactForm,
)
from .models import SingUp


def home(request):
    title = 'Sign Up Now'
    form = SingUpForm(request.POST or None)
    context = {
        'title': title,
        'form': form,
    }

    if form.is_valid():
        # print request.POST['email'] # not recommended
        instance = form.save(commit=False)

        full_name = form.cleaned_data.get('full_name')
        if not full_name:
            full_name = 'New full name'
        instance.full_name = full_name

        instance.save()
        context = {
            'title': 'Thank you'
        }

    if request.user.is_authenticated() and request.user.is_staff:
        queryset = SingUp.objects.all().order_by('-timestamp')
        # 特定の文字列が含まれている物を探す
        # queryset = SingUp.objects.all().order_by(
        #     '-timestamp').filter(full_name__icontains='2')
        context = {
            'queryset': queryset,
        }
    return render(request, 'newsletter/home.html', context)


def contact(request):
    title = 'Contact Us'
    form = ContactForm(request.POST or None)

    if form.is_valid():
        # for key, value in form.cleaned_data.iteritems():
        #     print key, value
        form_email = form.cleaned_data.get('email')
        form_message = form.cleaned_data.get('message')
        form_full_name = form.cleaned_data.get('full_name')

        subject = 'Site contact form'
        from_email = settings.EMAIL_HOST_USER
        to_email = form_email
        contact_message = '%s: %s via %s' % (
            form_full_name, form_message, form_email)

        send_mail(
            subject,
            contact_message,
            from_email,
            [to_email],
            fail_silently=True,
        )

    context = {
        'form': form,
        'title': title,
    }
    return render(request, 'newsletter/forms.html', context)


def about(request):

    return render(request, 'newsletter/about.html', {})
