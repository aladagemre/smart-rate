from django.db import models
from django import forms
import urllib
from django.template.defaultfilters import slugify
from member.models import UserProfile
from django.db.models import Count

class Category(models.Model):
	"""Category for the products"""
	name = models.CharField(max_length=20, unique=True)
	slug = models.SlugField()
	creator = models.ForeignKey(UserProfile, related_name='category_creator')
	last_activity = models.ForeignKey(UserProfile, related_name='category_last_editor')
	last_activity_time = models.DateTimeField(auto_now_add=True)
	created_time = models.DateTimeField(auto_now_add=True)

	def get_params(self):
	  return CategoryParameter.objects.filter(category=self)
	def __str__(self):
		return self.name
        

class CategoryParameter(models.Model):
	"""This is the abstract category parameter like Screen that belongs to all items from that category."""
	name = models.CharField(max_length=30)
	slug = models.SlugField()
	category = models.ForeignKey(Category)
	
	def __str__(self):
		return self.name
	
class Product(models.Model):
  slug = models.CharField(max_length=32, unique=True)
  name = models.CharField(max_length=32, unique=True)
  description = models.TextField()
  category = models.ForeignKey(Category)
  imgslug = models.CharField(max_length='256',null=True,blank=True)
  creator = models.ForeignKey(UserProfile, related_name='product_creator')
  last_activity = models.ForeignKey(UserProfile, related_name='product_last_editor')
  last_activity_time = models.DateTimeField(auto_now_add=True)
  created_time = models.DateTimeField(auto_now_add=True)
  
  def clean_fields(self, exclude=[]):
    self.name = self.name.strip()
    self.slug = urllib.quote(self.name.replace(' ','_').lower())
  def __str__(self):
    return self.name

class Parameter(models.Model):
  name = models.CharField(max_length=32)
  # "simple name", 
  #the name with _ and lowercase, used for ids and stuff
  slug = models.CharField(max_length=32) 
  #description = models.TextField()
  #category_parameter = models.ForeignKey(CategoryParameter)
  product = models.ForeignKey(Product)
  score_total = models.IntegerField(default=0)
  score_count = models.IntegerField(default=0)
  def slug_wo(self):
	return self.slug[1:]
  
  
  def __str__(self):
    return '%s - %s' % (self.product.name, self.category_parameter.name)
  def get_tags(self):
    return Tag.objects.filter(parameter = self)
  def get_tags_neg(self):
    #return Tag.objects.filter(parameter = self, charge=-1)
    return Tag.objects.filter(parameter=self, charge=-1).values('tagtext').order_by().annotate(Count('tagtext'))
    
  def get_tags_pos(self):
    #return Tag.objects.filter(parameter = self, charge=1)
    return Tag.objects.filter(parameter=self, charge=1).values('tagtext').order_by().annotate(Count('tagtext'))
  def get_score(self):
	if not self.score_count:
		return '-'
	return "%.2f" % (float(self.score_total) / self.score_count)
  
  @property
  def score(self): return self.get_score()
	
  

  def clean_fields(self, exclude=[]):
    self.category_parameter.name = self.category_parameter.name.strip()
    self.slug = self.category_parameter.name.replace(' ','_').lower()

class Tag(models.Model):
  tagtext = models.CharField(max_length=32)
  charge = models.IntegerField()
  parameter = models.ForeignKey(Parameter)
  author = models.ForeignKey(UserProfile)
  date = models.DateTimeField(auto_now_add=True)
  
  def __str__(self):
    return self.tagtext

class ProductForm(forms.ModelForm):
  class Meta:
    model = Product
    exclude = ['slug',]

class CategoryParameterForm(forms.ModelForm):
  class Meta:
    model = CategoryParameter
    #exclude = ('sname',)
    #fields = ('name','description')
    #fields = ('name', 'category')
    # I dont get it, when I exclude sname, I also can't use name parameterform.name in the template
  #description = forms.CharField(widget=forms.Textarea(attrs={'cols': 25, 'rows': 2}))
  
  
class TagForm(forms.ModelForm):
  class Meta:
    model = Tag
  #tagtext = forms.TextField(widget=forms.TextInput(attrs={'class':'taginput'}))
  tagtext = forms.CharField(widget=forms.TextInput(attrs={'class':'taginput', 'value':''}))

class CategoryForm(forms.ModelForm):
	class Meta:
		model = Category
		exclude=['slug']

# Create your models here.

class Score(models.Model):
  user = models.ForeignKey(UserProfile)
  value = models.IntegerField()
  param = models.ForeignKey(Parameter)
  
#import member.UserProfile
#class UserProfile(member.UserProfile):
  #pass