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
  """
  This view defined what to show in the index page. These are:
  Recent tags (ratings) and products
  """
  
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
  """
  Searches for the term given and returns the product results
  """
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
	"""
	Performs advanced search for the given parameters.
	With the parameters, it narrows down the results.
	"""
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
		Q(parameter__name=abstract_parameter) &
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
  """
  Displays product creation form or evaluates the posted form and saves the contents.
  """
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
  """
  This is for returning the information about a given product. 
  Returns name, parameter, tag, score information about it.
  """
  product = Product.objects.get(slug=path)
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
  """
  Allows rating a given parameter using a given score between 1 and 5.
  """
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

def create_parameter(request):
  """
  Allows creation of a new parameter for a given product.
  """
  productslug = request.POST['productslug']
  product = Product.objects.get(slug=productslug)
  d = copy.deepcopy(request.POST)
  param = Parameter(name=d['name'], slug='/'+slugify(d['name']), product=product)
  param.save()

  param.product.last_activity = request.user.userprofile
  param.product.save()

  
  return redirect('/products%s' % product.slug)

def ajax_createtag(request):
  """
  Allows creation of a new tag using Ajax requests.
  """
  tagtext = request.POST['tagtext']
  param = Parameter.objects.get(id=request.POST['parameter'])
  if type(request.user) is not AnonymousUser:
    tags_existing = Tag.objects.filter(tagtext=tagtext, author=request.user, parameter=param)
    # see if the user has used this tag before...
    if tags_existing:
      # if user has given this tag before for this parameter, return failure. He can't do this!
      return HttpResponse('failure')

  d = copy.deepcopy(request.POST)
  if request.user.is_authenticated():
    d['author'] = request.user.id
  else:
    d['author'] = 1

  # Create a new tag form for saving the tag.
  tagform = TagForm(d)
  user = request.user
  ty = type(user)

  Tag.objects.filter(author=request.user)
  post = request.POST
  tag = tagform.save()

  # Save this activity as the last activity for this product.
  tag.parameter.product.last_activity = request.user.userprofile
  tag.parameter.product.save()
  
  # if everything is fine so far, we've done!
  return HttpResponse('success')



def newcategory(request):
	"""
	Allows us to create a new category. 
	If no POST request is done, an empty form is provided for category creation.
	If POST request is done, a new category is created and the information is saved.
	"""
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
	"""
	Returns the category list
	"""
	categories = Category.objects.all()
	return render_to_response("categories.html", {
		'categories': categories,
	})
def category(request, slug):
	"""
	Displays the product list for a given category.
	"""
	category = Category.objects.get(slug=slug)
	products = Product.objects.filter(category=category)
	
	t = get_template("products_of_category.html")
	c = RequestContext(request,{})
	c['category'] = category
	c['products'] = products
	return HttpResponse(t.render(c))


import django.contrib.auth
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def login(request):
  """
  Lets the user to log in
  """
  username = request.POST['username']
  password = request.POST['password']
  path = request.POST['path']
  user = authenticate(username=username, password=password)
  print user
  if user is not None:
    django.contrib.auth.login(request, user)
  return HttpResponseRedirect(path)

def notable_for(request):
  """
  Fetches Freebase representation of a given product.
  """
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
	"""
	Returns RDF representation for the given product.
	"""
	print slug
	product = Product.objects.get(slug=slug)
	parameters = Parameter.objects.filter(product=product)
	return render_to_response("product.rdf", {
		'product': product,
		'parameters': parameters,
		
	})


@csrf_exempt
def add_product_fb(request):
  """
  Allows product addition using facebook account.
  """
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
	"""
	Lets you edit a category.
	"""
	t = get_template('edit_category.html')
	c = RequestContext(request,{})
	c['category'] = Category.objects.get(slug=slug)
	c['request'] = request
	c.update(csrf(request))
	return  HttpResponse(t.render(c))
 
def delete_category_parameter(request):
  """
  Lets you delete a parameter of a category"""
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
  """
  Lets you create a category parameter.
  """
  category_slug = request.POST['category_slug']
  parameter_name = request.POST['parameter_name']
  parameter_slug = '/'+slugify(parameter_name)
  
  
  cat = Category.objects.get(slug=category_slug)
  
  cat.last_activity = request.user.userprofile
  cat.save()

  
  CategoryParameter(category=cat, slug=parameter_slug, name=parameter_name).save()
  return HttpResponseRedirect('/edit_category'+category_slug)

def tag_count_of_user(userprofile):
  """
  Counts the tags assigned by a user.
  """
  return Tag.objects.filter(author=userprofile).count()

def products_rated_of_user(userprofile):
  """
  Returns the products rated by a given user.
  """
  scores = Score.objects.filter(user=userprofile)
  params = [x.param for x in scores]
  products = []
  for param in params:
	scs = Score.objects.filter(user=userprofile, param=param)
	if scs:
	  rating = scs[0]
	else:
	  rating = '-'
	d = {
	  'product' : param.product,
	  'rating' : scs,
	}
	products.append( d )
  return products

def user(request,username):
  """
  Displays information about a given user:
  Name, photo, tag count, products rated, followers, etc.
  """
  user_profile = User.objects.get(username	= username)
  t = get_template('user.html')
  c = RequestContext(request,{})
  
  is_owner = user_profile == request.user # see if we are the owner of this profile



  c['user_profile'] = user_profile
  c['request'] = request
  c['tagcount'] = tag_count_of_user(user_profile.userprofile)
  c['products'] = products_rated_of_user(user_profile.userprofile)
  c['is_owner'] = is_owner

  if request.user.is_authenticated():
    is_following = request.user.get_profile().following.filter(user__username = user_profile.username)
    following_list = user_profile.get_profile().following.all()
    follower_list = user_profile.get_profile().follower.all()
    c['is_following'] = is_following
    c['following_list'] = following_list
    c['follower_list'] = follower_list

  c.update(csrf(request))
  return  HttpResponse(t.render(c))

def follow(request, username):
	"""Lets the logged in user to follow the given username"""
	visitor_profile = request.user.get_profile()
	page_owner = User.objects.get(username=username)
	page_owner_profile = page_owner.get_profile()

	if not visitor_profile.following.filter(user = page_owner):
		visitor_profile.following.add(page_owner_profile)
	return HttpResponseRedirect('/user/%s' % username)

def unfollow(request, username):
	"""Lets the logged in user to unfollow the given username"""
        visitor_profile = request.user.get_profile()
        page_owner = User.objects.get(username=username)
        page_owner_profile = page_owner.get_profile()

        if visitor_profile.following.filter(user__username = page_owner.username):
                visitor_profile.following.remove(page_owner_profile)
	else:
		raise
        
	return HttpResponseRedirect('/user/%s' % username)