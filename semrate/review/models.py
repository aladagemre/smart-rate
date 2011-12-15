from django.db import models
from django import forms
import urllib

class Product(models.Model):
  suburi = models.CharField(max_length=32, unique=True)
  name = models.CharField(max_length=32, unique=True)
  description = models.TextField()
  def clean_fields(self, exclude=[]):
    self.name = self.name.strip()
    self.suburi = urllib.quote(self.name.replace(' ','_').lower())
  def __str__(self):
    return self.name

class Parameter(models.Model):
  name = models.CharField(max_length=32)
  # "simple name", 
  #the name with _ and lowercase, used for ids and stuff
  sname = models.CharField(max_length=32) 
  description = models.TextField()
  product = models.ForeignKey(Product)
  score_total = models.IntegerField(default=0)
  score_count = models.IntegerField(default=0)
  
  
  def __str__(self):
    return '%s - %s' % (self.product.name, self.name)
  def get_tags(self):
    return Tag.objects.filter(parameter = self)
  def get_tags_neg(self):
    return Tag.objects.filter(parameter = self, charge=-1)
  def get_tags_pos(self):
    return Tag.objects.filter(parameter = self, charge=1)
  def get_score(self):
	if not self.score_count:
		return 0
	return "%.2f" % (float(self.score_total) / self.score_count)
	
  def clean_fields(self, exclude=[]):
    self.name = self.name.strip()
    self.sname = self.name.replace(' ','_').lower()

class Tag(models.Model):
  tagtext = models.CharField(max_length=32)
  charge = models.IntegerField()
  parameter = models.ForeignKey(Parameter)
  def __str__(self):
    return self.tagtext

class ProductForm(forms.ModelForm):
  class Meta:
    model = Product
    exclude = ['suburi',]

class ParameterForm(forms.ModelForm):
  class Meta:
    model = Parameter
    exclude = ('sname',)
    #fields = ('name','description')
    # I dont get it, when I exclude sname, I also can't use name parameterform.name in the template
  description = forms.CharField(widget=forms.Textarea(attrs={'cols': 25, 'rows': 2}))
  
class TagForm(forms.ModelForm):
  class Meta:
    model = Tag
  #tagtext = forms.TextField(widget=forms.TextInput(attrs={'class':'taginput'}))
  tagtext = forms.CharField(widget=forms.TextInput(attrs={'class':'taginput', 'value':''}))



# Create your models here.



