# -*- coding: utf-8 -*-
import os
SETTINGS = 'settings'
os.environ['DJANGO_SETTINGS_MODULE'] = SETTINGS

from review.models import Product, Tag, Category, CategoryParameter, Parameter
from django.contrib.auth.models import User

try:
  bob = User(username='bob')
  bob.set_password('admin')
  bob.save()
  bob = bob.userprofile

  alice = User(username='alice')
  alice.set_password('admin')
  alice.save()
  alice = alice.userprofile
except:
  bob = User.objects.get(username='bob').userprofile
  alice = User.objects.get(username='alice').userprofile

Product.objects.all().delete()
Tag.objects.all().delete()
Category.objects.all().delete()
CategoryParameter.objects.all().delete()

c1 = Category(name='Mobile phone', slug='/user/robert/mobile_phones/mobile_phone', creator=alice, last_activity=alice)
c1.save()


c2 = Category(name='Hotel', slug='/travel/hotel', creator=bob, last_activity=bob)
c2.save()

cp11 = CategoryParameter(name='Battery', slug='/battery', category=c1)
cp11.save()

cp12 = CategoryParameter(name='Speed', slug='/speed', category=c1)
cp12.save()

cp21 = CategoryParameter(name='Breakfast', slug='/breakfast', category=c2)
cp21.save()

cp22 = CategoryParameter(name='Location', slug='/location', category=c2)
cp22.save()

cp32 = CategoryParameter(name='Room', slug='/room', category=c2)
cp32.save()


pr11 = Product(slug='/en/nokia_3210',name='Nokia 3210', description='Very fancy', category=c1, imgslug='/m/02bn_gl', creator=bob, last_activity=bob)
pr11.save()

pa111 = Parameter(slug='/battery',product=pr11)
pa111.save()

t1111 = Tag(tagtext='ugly',charge=-1, author=alice, parameter=pa111)
t1111.save()

t1112 = Tag(tagtext='long',charge=-1, author=alice, parameter=pa111)
t1112.save()

t1113 = Tag(tagtext='long',charge=-1, author=bob, parameter=pa111)
t1113.save()

t1113 = Tag(tagtext='big',charge=1, author=bob, parameter=pa111)
t1113.save()















