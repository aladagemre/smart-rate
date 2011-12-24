# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.template.loader import get_template
from django.core.context_processors import csrf
from django.db.models import Q
from django.shortcuts import render_to_response, redirect
from models import * #Product, ProductForm, Parameter, Category, CategoryParameter, CategoryParameterForm, Tag, TagForm
import copy
from django.template.defaultfilters import slugify
from django.contrib.auth.models import AnonymousUser
def index(request):
  recent_tags = Tag.objects.order_by('date')[::-1]
  recent_products = map(lambda tag: tag.parameter.product, recent_tags)
  recent_authors = map(lambda tag: tag.author.user.username, recent_tags)
  recent_dates = map(lambda tag: tag.date, recent_tags)
  
  product_set = []
  author_set = []
  date_set = []
  suburi_set = []
  for i, product in enumerate(recent_products):
    if product not in product_set:
      product_set.append(product)
      author_set.append(recent_authors[i])
      date_set.append(recent_dates[i])

  recent_pair = zip(product_set, author_set, date_set)

  t = get_template('index.html')
  c = RequestContext(request,{})
  c['request'] = request
  c['products'] = Product.objects.all()
  c['recent_pair'] = recent_pair
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
  # get abstract category parameter of each parameter. (like screen of iphone -> screen)
  parameter_c_values = set(map(lambda p: p.category_parameter, parameters))
  # get abstract category parameter of this type of product (cell phone)
  category_parameters = set(CategoryParameter.objects.filter(category=product.category))
  
  # see if we have any missing feature for iphone.
  lacking_c_parameters = category_parameters - parameter_c_values
  
  # if we have any missing parameter(feature) for iphone then add it.
  # for example after creating iphone, you created samsung and added new features to samsung. now you want iphone to have those features too.
  # so lets add those missing features:
  
  if lacking_c_parameters:
    # for each missing feature
    for c_param in lacking_c_parameters:
      slug = slugify(c_param.name)
      p = Parameter(sname=slug, category_parameter=c_param, product=product, score_total=0, score_count=0)
      p.save()
    
    # now get the updated parameter list for iphone. 
    parameters = Parameter.objects.filter(product=product)

  score_total = 0
  score_count = 0
  for parameter in parameters:
    score_total += parameter.score_total
    score_count += parameter.score_count
  if not score_count:
    overall_score = 0
  else:
    overall_score = score_total / float(score_count)
  
  t = get_template('viewproduct.html')
  c = RequestContext(request,{})
  c['request'] = request
  c['product'] = product
  c['parameters'] = parameters
  c['parameterform'] = CategoryParameterForm()
  c['tagform'] = TagForm()
  c['overall_score'] = overall_score
  c.update(csrf(request))
  return  HttpResponse(t.render(c))
  
def rate_parameter(request):
  score = int ( request.GET['score'] )
  param_id = int ( request.GET['parameter_id'] )
  parameter = Parameter.objects.get(id=param_id)
  parameter.score_total += score
  parameter.score_count += 1
  parameter.save()
  product = parameter.product
  
  return redirect('/products/%s' % product.suburi)
"""  
def ajax_createparameter(request):
  parameterform = CategoryParameterForm(request.POST)
  stuff = dir(parameterform)
  errors = parameterform.errors
  parameterform.save()
  return HttpResponse('success')
"""
def create_parameter(request):
  product = Product.objects.get(id=int(request.POST.get('product')))
  d = copy.deepcopy(request.POST)
  del d['product']
  parameterform = CategoryParameterForm(d)
  stuff = dir(parameterform)
  errors = parameterform.errors
  parameterform.save()
  
  return redirect('/products/%s' % product.suburi)


def ajax_createtag(request):
  tagtext = request.POST['tagtext']
  if type(request.user) is not AnonymousUser:
    tags_existing = Tag.objects.filter(tagtext=tagtext, author=request.user)
    if tags_existing:
      return HttpResponse('failure')

  d = copy.deepcopy(request.POST)
  if request.user.is_authenticated():
    d['author'] = request.user.id
  else:
    d['author'] = 1

  tagform = TagForm(d)
  #tag = tagform.save(commit=False)
  #tag.parameter = Parameter.objects.get(name=request.POST['parametername'])
  #tag.parameter = Parameter.objects.get(name='monitor')
  #tagform.parameter = 2 #Parameter.objects.all()[0]
  #tagform.charge = 1 #Parameter.objects.all()[0]
  tagform.save()
  #raise
  return HttpResponse('success')



def newcategory(request):
	if 'submit' in request.POST:
		slug = slugify(request.POST['name'])
		d = copy.deepcopy(request.POST)
		d['slug'] = slug
		categoryform = CategoryForm(d)
		if categoryform.is_valid():
			c = categoryform.save()
			return HttpResponseRedirect('/categories')

	else:
		categoryform = CategoryForm()
	
	t = get_template('newcategory.html')
	c = RequestContext(request,{})
	c['categoryform'] = categoryform
	c['request'] = request
	c.update(csrf(request))
	return  HttpResponse(t.render(c))
	
def categories(request):
	categories = Category.objects.all()
	return render_to_response("categories.html", {
		'categories': categories,
	})
def category(request, slug):
	category = Category.objects.get(slug=slug)
	products = Product.objects.filter(category=category)
	
	return render_to_response("products_of_category.html", {
		'category': category,
		'products': products,
	})
	