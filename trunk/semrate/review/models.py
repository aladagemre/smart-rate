from django.db import models
from django import forms
import urllib
from django.template.defaultfilters import slugify
from member.models import UserProfile
from django.db.models import Count

class Category(models.Model):
	"""
	Category class for the products. Each product might belong to one category.
	Categories can be Mobile Phones, Automobiles, etc.
	"""
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
	"""
	This is the abstract category parameter like Screen that belongs to all items from that category.
	"""
	name = models.CharField(max_length=30)
	slug = models.SlugField()
	category = models.ForeignKey(Category)
	
	def __str__(self):
		return self.name
	
class Product(models.Model):
  """
  This is the class for Product or Services that is going to be rated.
  """
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
  """
  This is the class for the parameter for a product. Like Screen or Battery.
  """
  name = models.CharField(max_length=32)
  slug = models.CharField(max_length=32)  # short name
  product = models.ForeignKey(Product)    # foreign key to product.
  score_total = models.IntegerField(default=0)		# total scores given by users.
  score_count = models.IntegerField(default=0)		# total number of votes
  
  def slug_wo(self):
	return self.slug[1:]
  
  
  def __str__(self):
    """
    String representaton of the parameter.
    """
    return '%s - %s' % (self.product.name, self.category_parameter.name)
    
  def get_tags(self):
    """
    Returns the tags tagged for this parameter
    """
    return Tag.objects.filter(parameter = self)
    
  def get_tags_neg(self):
    """
    Returns the negative tags tagged for this parameter
    """

    return Tag.objects.filter(parameter=self, charge=-1).values('tagtext').order_by().annotate(Count('tagtext'))
    
  def get_tags_pos(self):
    """
    Returns the positive tags tagged for this parameter
    """
    return Tag.objects.filter(parameter=self, charge=1).values('tagtext').order_by().annotate(Count('tagtext'))
    
  def get_score(self):
    """
    Returns the average score by a simple calculation.
    """
    if not self.score_count:
      return '-'
    return "%.2f" % (float(self.score_total) / self.score_count)
  
  @property
  def score(self):
    """
    This is just for allowing template to use calculated average score.
    """
    return self.get_score()  

  def clean_fields(self, exclude=[]):
    self.category_parameter.name = self.category_parameter.name.strip()
    self.slug = self.category_parameter.name.replace(' ','_').lower()

class Tag(models.Model):
  """
  This is the tag assignment that is done to the parameters of products. 
  Each tag has an author(tagger), date, text, charge(+/-) and parameter(tagged object)
  """
  tagtext = models.CharField(max_length=32)
  charge = models.IntegerField()
  parameter = models.ForeignKey(Parameter)
  author = models.ForeignKey(UserProfile)
  date = models.DateTimeField(auto_now_add=True)
  
  def __str__(self):
    return self.tagtext

class ProductForm(forms.ModelForm):
  """
  This class provides information about what to show in a product creation form.
  """
  
  class Meta:
    model = Product
    exclude = ['slug',]

class CategoryParameterForm(forms.ModelForm):
  """
  This class provides information about what to show in a product parameter creation form.
  """
  class Meta:
    model = CategoryParameter  
  
class TagForm(forms.ModelForm):
  """
  This class provides information about what to show in a Tag creation form.
  """
  class Meta:
    model = Tag
  tagtext = forms.CharField(widget=forms.TextInput(attrs={'class':'taginput', 'value':''}))

class CategoryForm(forms.ModelForm):
	"""
	This class provides information about what to show in a category creation form.
	"""
	class Meta:
		model = Category
		exclude=['slug']

# Create your models here.

class Score(models.Model):
  """
  This class is for handling number of ratings individually.
  """
  user = models.ForeignKey(UserProfile)
  value = models.IntegerField()
  param = models.ForeignKey(Parameter)