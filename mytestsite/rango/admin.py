from django.contrib import admin
from rango.models import Category, Page, UserProfile

# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
    fields = ['likes', 'views', 'name']
    #prepopulated_field = {'slug': ('name',)} 


class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'url')


admin.site.register(Category, CategoryAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(UserProfile)

