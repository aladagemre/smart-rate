# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.template.loader import get_template
from django.core.context_processors import csrf
from django.db.models import Q
from django.shortcuts import render_to_response
from models import Product, ProductForm, Parameter, ParameterForm, Tag, TagForm

def index(request):
  t = get_template('index.html')
  c = RequestContext(request,{})
  c['request'] = request
  c['products'] = Product.objects.all()
  return  HttpResponse(t.render(c))

def searchproduct(request):
  query = request.GET.get('q', '')
  if query:
    qset = (
      Q(name__icontains=query) |
      Q(description__icontains=query)
    )
    results = Product.objects.filter(qset).distinct()
  else:
    results = []
  
  return render_to_response("search.html", {
    "results": results,
    "query": query
  })

def newproduct(request):
  if 'submit' in request.POST:
    productform = ProductForm(request.POST)
    if productform.is_valid():
      p = productform.save()
      return HttpResponseRedirect('/products/%s' % p.suburi)
    
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
  c['tagform'] = TagForm()
  c.update(csrf(request))
  return  HttpResponse(t.render(c))
  

def ajax_createparameter(request):
  parameterform = ParameterForm(request.POST)
  stuff = dir(parameterform)
  errors = parameterform.errors
  parameterform.save()
  return HttpResponse('success');

def ajax_createtag(request):
  tagform = TagForm(request.POST)
  #tag = tagform.save(commit=False)
  #tag.parameter = Parameter.objects.get(name=request.POST['parametername'])
  #tag.parameter = Parameter.objects.get(name='monitor')
  #tagform.parameter = 2 #Parameter.objects.all()[0]
  #tagform.charge = 1 #Parameter.objects.all()[0]
  tagform.save()
  return HttpResponse('success')


