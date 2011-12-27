# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.core.context_processors import csrf
from django.template.loader import get_template
from django.db.models import Q
from django.shortcuts import render_to_response, redirect
from models import * #Product, ProductForm, Parameter, Category, CategoryParameter, CategoryParameterForm, Tag, TagForm
import copy
from django.template.defaultfilters import slugify
from django.contrib.auth.models import AnonymousUser, User
from django.db.models import F
import json, urllib, urllib2, datetime

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
  c['facebook_id'] = getattr(request.user, 'userprofile', None)
 
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

def advanced_search(request):
	category=request.GET.get('category')
	categories = Category.objects.all()
	if category:
		parameters = CategoryParameter.objects.filter(category__name=category)
		for c in categories:
			if c.name == category:
				c.selected = True
			
		d = { 'categories': categories, 'parameters': parameters, 'category': category }
	else:
		d = { 'categories': categories }
	
	abstract_parameter = request.GET.get('parameter')
	min_rating = request.GET.get('min')
	max_rating = request.GET.get('max')
	if abstract_parameter and min_rating and max_rating:
		qset = (
		Q(category__name=category) &
		Q(parameter__category_parameter__name=abstract_parameter) &
		Q(parameter__score_total__gte=F('parameter__score_count')*float(min_rating)) &
		Q(parameter__score_total__lte=F('parameter__score_count')*float(max_rating)) 
		)
		results = Product.objects.filter(qset).distinct()		
		d['results']=results
		d['min'] = min_rating
		d['max'] = max_rating
		d['parameter'] = abstract_parameter
		
		
		
	return render_to_response("advanced_search.html",d)
		

def newproduct(request):
  if 'submit' in request.POST:
    productform = ProductForm(request.POST)
    if productform.is_valid():
      p = productform.save()
      return HttpResponseRedirect('/products/%s' % p.slug)
    
  else:
    productform = ProductForm()
  t = get_template('newproduct.html')
  c = RequestContext(request,{})
  c['productform'] = productform
  c['request'] = request
  c.update(csrf(request))

  return  HttpResponse(t.render(c))

def viewproduct(request, path):
  product = Product.objects.get(slug=path)
  #parameters = Parameter.objects.filter(product=product)
  ## get abstract category parameter of each parameter. (like screen of iphone -> screen)
  #parameter_c_values = set(map(lambda p: p.category_parameter, parameters))
  ## get abstract category parameter of this type of product (cell phone)
  #category_parameters = set(CategoryParameter.objects.filter(category=product.category))
  
  ## see if we have any missing feature for iphone.
  #lacking_c_parameters = category_parameters - parameter_c_values
  
  ## if we have any missing parameter(feature) for iphone then add it.
  ## for example after creating iphone, you created samsung and added new features to samsung. now you want iphone to have those features too.
  ## so lets add those missing features:
  
  #if lacking_c_parameters:
    ## for each missing feature
    #for c_param in lacking_c_parameters:
      #slug = slugify(c_param.name)
      #p = Parameter(slug=slug, category_parameter=c_param, product=product, score_total=0, score_count=0)
      #p.save()
    
    ## now get the updated parameter list for iphone. 
  parameters = Parameter.objects.filter(product=product)

  score_total = 0
  score_count = 0
  for parameter in parameters:
    score_total += parameter.score_total
    score_count += parameter.score_count
  if not score_count:
    overall_score = '-'
  else:
    overall_score = '%.1f'%(score_total / float(score_count))
  
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
  param = Parameter.objects.get(id=param_id)
  
  if Score.objects.filter(param=param,user=request.user.userprofile):
	sc = Score.objects.get(param=param, user=request.user.userprofile)
	sc.value = score
	sc.save()
  else:
	Score(param=param, value=score, user = request.user.userprofile).save()

  scs = Score.objects.filter(param=param)
  
  param.product.last_activity = request.user.userprofile
  param.product.save()
  
  param.score_total = sum([sc.value for sc in scs])
  param.score_count = len(scs)
  param.save()
  product = param.product
  
  
  
  return redirect('/products%s' % product.slug)
"""  
def ajax_createparameter(request):
  parameterform = CategoryParameterForm(request.POST)
  stuff = dir(parameterform)
  errors = parameterform.errors
  parameterform.save()
  return HttpResponse('success')
"""
def create_parameter(request):
  productslug = request.POST['productslug']
  print productslug
  product = Product.objects.get(slug=productslug)
  d = copy.deepcopy(request.POST)
  #del d['product']
  #product = Product.objects.get(slug=d['productslug'])
  ##d['slug'] = slugify(d['name'])
  #parameterform = CategoryParameterForm(d)
  #stuff = dir(parameterform)
  #errors = parameterform.errors
  #parameterform.save()
  param = Parameter(name=d['name'], slug='/'+slugify(d['name']), product=product)
  param.save()

  param.product.last_activity = request.user.userprofile
  param.product.save()

  
  return redirect('/products%s' % product.slug)

def ajax_createtag(request):
  tagtext = request.POST['tagtext']
  param = Parameter.objects.get(id=request.POST['parameter'])
  if type(request.user) is not AnonymousUser:
    tags_existing = Tag.objects.filter(tagtext=tagtext, author=request.user, parameter=param)
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
  user = request.user
  ty = type(user)

  Tag.objects.filter(author=request.user)
  post = request.POST
  tag = tagform.save()

  tag.parameter.product.last_activity = request.user.userprofile
  tag.parameter.product.save()

  #raise
  return HttpResponse('success')



def newcategory(request):
	if 'submit' in request.POST:
		slug = '/'+slugify(request.POST['name'])
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
	
	t = get_template("products_of_category.html")
	c = RequestContext(request,{})
	c['category'] = category
	c['produccts'] = products
	return HttpResponse(t.render(c))


import django.contrib.auth
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def login(request):
  username = request.POST['username']
  password = request.POST['password']
  path = request.POST['path']
  user = authenticate(username=username, password=password)
  print user
  if user is not None:
    django.contrib.auth.login(request, user)
  return HttpResponseRedirect(path)

def notable_for(request):
  id = request.GET['id']
  #id = "/en/nokia_3210"
  q = { "extended":1, "query": { "id": id, "type": "/common/topic", "notable_for": None } }
  q_json = json.dumps(q)

  url = 'http://www.freebase.com/api/service/mqlread?query=%s' % q_json
  req = urllib2.Request(url=url)
  s = urllib2.urlopen(req).read()
  res = json.loads(s)

  notable_for = res['result']['notable_for']

  q = { "extended":1, "query": { "id": notable_for, "name": None} }
  q_json = json.dumps(q)
  url = 'http://www.freebase.com/api/service/mqlread?query=%s' % q_json
  req = urllib2.Request(url=url)
  s = urllib2.urlopen(req).read()
  res = json.loads(s)

  type_name = res['result']['name']

  response_json = json.dumps({"id":notable_for, "name":type_name})

  
  return HttpResponse(response_json, content_type='application/json')
  
  
def rdf(request, slug):
	product = Product.objects.get(slug=slug)
	parameters = Parameter.objects.filter(product=product)
	return render_to_response("product.rdf", {
		'product': product,
		'parameters': parameters,
		
	})


@csrf_exempt
def add_product_fb(request):
  fbid = request.POST['fbid']
  fbname = request.POST['fbname']
  fbtype_id = request.POST['fbtype_id']
  fbtype_name = request.POST['fbtype_name']
  imgslug = request.POST['imgslug']
  up = request.user.userprofile
  dt = datetime.datetime.now()
  
  if not Category.objects.filter(slug=fbtype_id):
	c = Category(name=fbtype_name, slug=fbtype_id, creator=up, last_activity=up, last_activity_time=dt)
	c.save()
  else:
	c = Category.objects.get(slug=fbtype_id)
  if not Product.objects.filter(slug=fbid):
	p = Product(slug=fbid, name=fbname, description='x', category=c, imgslug=imgslug, creator=up, last_activity=up, last_activity_time=dt)
	p.save()
  else:
	p = Product.objects.get(slug=fbid)

  l = CategoryParameter.objects.filter(category=c)
  print c
  print l
  for param in l:
	Parameter(name=param.name, slug=param.slug, product=p).save()
  
	
  return HttpResponseRedirect('/products'+fbid)
  #return HttpResponse('foo')
  
  
  
def edit_category(request,slug):
	t = get_template('edit_category.html')
	c = RequestContext(request,{})
	c['category'] = Category.objects.get(slug=slug)
	c['request'] = request
	c.update(csrf(request))
	return  HttpResponse(t.render(c))
 
def delete_category_parameter(request):
  category_slug = request.GET['category_slug']
  parameter_slug = request.GET['parameter_slug']
  cat = Category.objects.get(slug=category_slug)
  CategoryParameter.objects.get(category=cat, slug=parameter_slug).delete()
  s = CategoryParameter.objects.filter(category=cat, slug=parameter_slug).__str__()
  #s = Category.objects.filter(slug=category_slug).__str__()
  #return HttpResponse(s, content_type='text/plain')
  return HttpResponseRedirect('/edit_category'+category_slug)
  
@csrf_exempt
def create_category_parameter(request):
  category_slug = request.POST['category_slug']
  parameter_name = request.POST['parameter_name']
  parameter_slug = '/'+slugify(parameter_name)
  
  
  cat = Category.objects.get(slug=category_slug)
  
  cat.last_activity = request.user.userprofile
  cat.save()

  
  CategoryParameter(category=cat, slug=parameter_slug, name=parameter_name).save()
  return HttpResponseRedirect('/edit_category'+category_slug)

def tag_count_of_user(userprofile):
  return Tag.objects.filter(author=userprofile).count()

def products_rated_of_user(userprofile):
  scores = Score.objects.filter(user=userprofile)
  params = [x.param for x in scores]
  products = [param.product for param in params]
  return products

def user(request,username):
  user = User.objects.get(username	= username)
  t = get_template('user.html')
  c = RequestContext(request,{})
  
  
  c['user'] = user
  c['request'] = request
  c['tagcount'] = tag_count_of_user(user.userprofile)
  c['products'] = products_rated_of_user(user.userprofile)
  c.update(csrf(request))
  return  HttpResponse(t.render(c))
  