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
  description = models.TextField()
  product = models.ForeignKey(Product)
  def __str__(self):
    return self.name
  def get_tags(self):
    return Tag.objects.filter(parameter = self)
  def get_tags_neg(self):
    return Tag.objects.filter(parameter = self, charge=-1)
  def get_tags_pos(self):
    return Tag.objects.filter(parameter = self, charge=1)


class Tag(models.Model):
  tagtext = models.CharField(max_length=32)
  charge = models.IntegerField()
  parameter = models.ForeignKey(Parameter)
  def __str__(self):
    return self.tagtext

class ProductForm(forms.ModelForm):
  class Meta:
    model = Product
    exclude = ['suburi']

class ParameterForm(forms.ModelForm):
  class Meta:
    model = Parameter
    #exclude = ('product',)
  description = forms.CharField(widget=forms.Textarea(attrs={'cols': 25, 'rows': 2}))
  
class TagForm(forms.ModelForm):
  class Meta:
    model = Tag



# Create your models here.
