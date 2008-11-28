# Create your views here.

from django.template import loader
from django.http import HttpResponse

from django.shortcuts import render_to_response
import djweb.settings as settings
import djweb.mainsite.models as models

def trunkpage(request, trail):
    x = loader.render_to_string('frontpage.html', {'trail':trail, 'settings':settings})
    return HttpResponse(x)


    t = template_loader.get_template('frontpage.html')
    c = template.Context({'trail':trail, 'settings':settings })
    return HttpResponse(t.render(c))
    return render_to_response('frontpage.html', {'trail':trail, 'settings':settings})



