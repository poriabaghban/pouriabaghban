from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ContactForm


def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "فرم شما با موفقیت ارسال شد. حتماً باهاتون تماس می‌گیریم.")
            return redirect("contact:contact")
        else:
            messages.error(request, "ارسال فرم ناموفق بود. لطفاً اطلاعات را درست وارد کنید.")
    else:
        form = ContactForm()

    context = {
        "form": form,
    }

    return render(request, "contact/contact.html", context)