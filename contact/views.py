from django.shortcuts import render, redirect
from django.contrib import messages
from .models import ContactMessage, ContactSetting
from .forms import ContactForm

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'پیام شما با موفقیت ارسال شد!')
            return redirect('contact:contact')
    else:
        form = ContactForm()
    
    try:
        settings = ContactSetting.objects.first()
    except:
        settings = None
    
    context = {
        'form': form,
        'settings': settings,
        'title': 'تماس با ما'
    }
    return render(request, 'contact/contact.html', context)
