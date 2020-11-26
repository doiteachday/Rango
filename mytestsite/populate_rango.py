# automate populate database with data.
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'mytestsite.settings')

import django
django.setup()
from rango.models import Category, Page

def populate():
    python_pages=[
            {"title": "Python Tutorial",
                "url": "http://docs.python.org/2/tutorial/",
                "views": 33},
            {"title": "How to Think Like a Computer Scientist",
                "url": "httpp://www.greenteapress.com/thinkpython",
                "views": 31},
            {"title": "Learn Python",
                "url": "http://www.learnpython.org",
                "views": 30}]

    django_pages=[
            {"title": "Django Tutorial",
                "url": "https://docs.djangoproject.com",
                "views": 29},
            {"title": "Django Rocks",
                "url": "http://www.djangorocks.com/",
                "views": 28},
            {"title": "How to Tango with Django",
                "url": "http://www.tangowithdjango.com/",
                "views": 27}]

    other_pages=[
            {"title": "Bottle",
                "url": "http://bottlepy.org/docs/dev/",
                "views": 27},
            {"title": "Flask",
                "url": "http://flask.pocoo.org",
                "views": 26}]

    cats = {"Python": {"pages": python_pages},
            "Django": {"pages": django_pages},
            "Other Frameworks": {"pages": other_pages}}

    for cat, cat_data in cats.items():
        c = add_cat(cat)
        for p in cat_data["pages"]:
            add_page(c, p["title"], p["url"], p["views"])

    # print out the categories we have added.
    for c in Category.objects.all():
        for p in Page.objects.filter(category=c):
            print("- {0} - {1}".format(str(c), str(p)))


def add_page(cat, title, url, views):
    p = Page.objects.get_or_create(category=cat, title=title)[0]
    p.url=url
    p.views=views
    p.save()
    return p

def add_cat(name, views=0, likes=0):
    if name == "Python":
        views, likes = 128, 64
    elif name == "Django":
        views, likes = 64, 32
    else:
        views, likes = 32, 16
    c = Category.objects.get_or_create(name=name)[0]
    c.views = views
    c.likes = likes
    c.save()
    return c

# Start execution here!
if __name__ == '__main__':
    print("Starting Rango population script...")
    populate()







