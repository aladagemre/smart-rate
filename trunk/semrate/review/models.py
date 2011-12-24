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

	def __str__(self):
		return self.name		
        

class CategoryParameter(models.Model):
	"""This is the abstract category parameter like Screen that belongs to all items from that category."""
	name = models.CharField(max_length=30)
	category = models.ForeignKey(Category)
	
class Product(models.Model):
  suburi = models.CharField(max_length=32, unique=True)
  name = models.CharField(max_length=32, unique=True)
  description = models.TextField()
  category = models.ForeignKey(Category)
  
  def clean_fields(self, exclude=[]):
    self.name = self.name.strip()
    self.suburi = urllib.quote(self.name.replace(' ','_').lower())
  def __str__(self):
    return self.name

class Parameter(models.Model):
  #name = models.CharField(max_length=32)
  # "simple name", 
  #the name with _ and lowercase, used for ids and stuff
  sname = models.CharField(max_length=32) 
  #description = models.TextField()
  category_parameter = models.ForeignKey(CategoryParameter)
  product = models.ForeignKey(Product)
  score_total = models.IntegerField(default=0)
  score_count = models.IntegerField(default=0)
  
  
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
		return 0
	return "%.2f" % (float(self.score_total) / self.score_count)
	
	
  

  def clean_fields(self, exclude=[]):
    self.category_parameter.name = self.category_parameter.name.strip()
    self.sname = self.category_parameter.name.replace(' ','_').lower()

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
    exclude = ['suburi',]

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

# Create your models here.


