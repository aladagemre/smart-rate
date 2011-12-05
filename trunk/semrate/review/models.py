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

class Tag(models.Model):
  tagtext = models.CharField(max_length=32)
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
  
  

# Create your models here.
