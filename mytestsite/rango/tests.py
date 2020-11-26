from django.test import TestCase
from django.urls import reverse
from rango.models import Category


class CategoryMethodTests(TestCase):
    def test_ensure_views_are_positive(self):
        """
        return: True
        category.views >= 0
        """
        cat = Category(name='test', views=-1, likes=0)
        cat.save()
        self.assertEqual((cat.views >= 0), True)


    def test_slug_line_creation(self):
        """
        check a category slug is created.
        """
        cat = Category(name='python three')
        cat.save()
        self.assertEqual(cat.slug, 'python-three')


def add_category(name, views, likes):
    """ add category to database"""
    cat = Category.objects.get_or_create(name=name)[0]
    cat.views = views
    cat.likes = likes
    cat.save()
    return cat


class IndexViewTests(TestCase):
    def test_index_view_with_no_categories(self):
        """
        if no categories, an appropiate message should be display.
        """
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "There are no categories present.")
        self.assertQuerysetEqual(response.context['categories'], [])


    def test_index_view_with_categories(self):
        """
        check the index has categories displayed.
        """

        add_category('test', 1, 1)
        add_category('est', 1, 1)
        add_category('st', 1, 1)
        add_category('t', 1, 1)

        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'test est st')

        num_cats = len(response.context['categories'])
        self.assertEqual(num_cats, 4)



