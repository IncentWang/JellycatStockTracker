from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
import requests
from .watchform import Watchform
from StockTracker.models import User, Toy, Watching
from StockTracker.website_info import Website_info
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect
from multiprocessing import Process
from long_polling_deamon import SendConfirmationEmail
import time

# Create your views here.
def index(request):
    return HttpResponse("Hello world. You are in StockTracker index page.")

def success(request):
    return render(request, "success.html")

def startwatch(request):
    if request.method == "POST":
        form = Watchform(request.POST)
        if form.is_valid():
            # Do main logic here
            url = form.cleaned_data['url']
            sku = form.cleaned_data['sku'].lower()
            email = form.cleaned_data['email']

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                user = User(email=email)
                user.save()

            winfo = Website_info(url, sku)
            try:
                winfo.get_info_from_url()
            except requests.exceptions.ConnectionError:
                return HttpResponse("<script type=\"text/javascript\">alert(\"Cannot fetch Jellycat data from URL you input, please check if URL is correct and try again.\"); window.location = \"{}\";</script>".format("/stocktracker/startwatch"))
            except IndexError:
                return HttpResponse("<script type=\"text/javascript\">alert(\"Cannot fetch information of SKU you input, please check if the SKU is correct and URL is correct and try again.\"); window.location = \"{}\";</script>".format("/stocktracker/startwatch"))
            
            try:
                if not winfo.check_stock():
                    try:
                        toy = Toy.objects.get(sku=sku, url=url)
                    except Toy.DoesNotExist:
                        toy = Toy(sku=sku, url=url, name=winfo.get_name())
                        toy.save()
                    
                    try:
                        watch = Watching.objects.get(user=user, watched_toy=toy)
                        messages.error(request, "you have added this watch before, we will send you email when restock")
                    except Watching.DoesNotExist:
                        watch = Watching(user=user, watched_toy=toy, start_time=timezone.now(), get_result=False)
                        watch.save()
                        p = Process(target=SendConfirmationEmail, args=(user.email, toy.name, toy.sku))
                        p.start()
                        p.join()
                        return HttpResponseRedirect("/stocktracker/success")
            except KeyError:
                return HttpResponse("<script type=\"text/javascript\">alert(\"Cannot fetch information of SKU you input, please check if the SKU is correct and URL is correct and try again.\"); window.location = \"{}\";</script>".format("/stocktracker/startwatch"))
            else:
                return HttpResponse("<script type=\"text/javascript\">alert(\"The JellyCat you want to watch is still in stock! Close this window to redirect to offical website to buy.\"); window.location = \"{}\";</script>".format(winfo.url))
    else:
        form = Watchform()

    return render(request, "new_watch.html", {'form' : form})
