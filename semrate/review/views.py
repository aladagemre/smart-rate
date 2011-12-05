# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.template.loader import get_template
from django.core.context_processors import csrf

from models import Product, ProductForm, Parameter, ParameterForm

def index(request):
  t = get_template('index.html')
  c = RequestContext(request,{})
  c['request'] = request
  c['products'] = Product.objects.all()
  return  HttpResponse(t.render(c))

def newproduct(request):
  if 'submit' in request.POST:
    productform = ProductForm(request.POST)
    if productform.is_valid():
      p = productform.save()
      return HttpResponseRedirect('/%s' % p.suburi)
    
  else:
    productform = ProductForm()
  t = get_template('newproduct.html')
  c = RequestContext(request,{})
  c['productform'] = productform
  c['request'] = request
  c.update(csrf(request))

  return  HttpResponse(t.render(c))

def viewproduct(request, path):
  product = Product.objects.get(suburi=path)
  parameters = Parameter.objects.filter(product=product)


  t = get_template('viewproduct.html')
  c = RequestContext(request,{})
  c['request'] = request
  c['product'] = product
  c['parameters'] = parameters
  c['parameterform'] = ParameterForm()
  c.update(csrf(request))
  return  HttpResponse(t.render(c))
  

def ajax_createparameter(request):
  parameterform = ParameterForm(request.POST)
  parameterform.save()
  return HttpResponse('success');
