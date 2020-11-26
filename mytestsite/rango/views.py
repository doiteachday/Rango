from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from rango.models import Category, Page, User, UserProfile
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from datetime import datetime
from rango.bing_search import run_query


# Create your views here.
def index(request):
    request.session.set_test_cookie()
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]

    context_dict = {'categories': category_list, 'pages': page_list}

    # handle the cookie
    visitor_cookie_handler(request)
    context_dict['visits'] = request.session['visits']
    context_dict['last_visit'] = request.session['last_visit']

    #obtain response object early
    response = render(request, 'rango/index.html', context=context_dict)

    # return response to user, updating any cookie that need changed.
    return response


def about(request):
    if request.session.test_cookie_worked():
        print("TEST COOKIE WORKED")
        request.session.delete_test_cookie()

    # the request method is GET/POST
    print(request.method)
    # no user, show 'AnonymousUser'
    print(request.user)

    # handle the cookie
    visitor_cookie_handler(request)
    context_dict = {}
    context_dict['visits'] = request.session['visits']
    context_dict['last_visit'] = request.session['last_visit']

    response =  render(request, 'rango/about.html', context=context_dict)
    return response


def show_category(request, category_name_slug):
    #Create a context dictionary which we can pass to
    #the template rendering engine.
    context_dict = {}

    try:
        # Find a category name slug with the given name?
        # the .get() method returns one model instance or raise an exception.
        category = Category.objects.get(slug=category_name_slug)

        # Retrive all of the associated pages.
        pages = Page.objects.filter(category=category).order_by('-views')

        # Adds the results list(pages) to the template context under name pages.
        context_dict['pages'] = pages
        context_dict['category'] = category
    except Category.DoesNotExist:
        # We get here if we didn't find the specified category.
        # Don't do anything.
        context_dict['category'] = None
        context_dict['pages'] = None

    # Go render the response and return it to the client.
    return render(request, 'rango/category.html', context_dict)


@login_required
def add_category(request):
    form = CategoryForm()

    # A HTTP POST?
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        # a valid form?
        if form.is_valid():
            # Save the new category to database.
            form.save(commit=True)
            #cat = form.save(commit=True)
            #print(cat, cat.slug)
            return index(request)
        else:
            print(form.errors)

    return render(request, 'rango/add_category.html', {'form': form})


@login_required
def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    form = PageForm
    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if category:
                page  = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
                return show_category(request, category_name_slug)
        else:
            print(form.errors)

    context_dict = {'form': form, 'category': category}
    return render(request, 'rango/add_page.html', context_dict)


"""
def register(request):
    # A boolean value for telling the template whether the registration was success.
    registered = False

    # if request.POST, then process form data.
    if request.method == 'POST':
        # Attempt to grab information from the raw form information.
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        # if the two forms are valid
        if user_form.is_valid() and profile_form.is_valid():
            # save the user's form data to database.
            user = user_form.save()

            # hash the password with the set_password method and update the user object.
            user.set_password(user.password)
            user.save()

            # the "commit"delays saving the model.
            profile = profile_form.save(commit=False)
            profile.user = user

            # profile picture provided?
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            # save the UserProfile model instance.
            profile.save()

            # indicate that the template registration was successful.
            registered = True
        else:
            # invalid forms and show the problems.
            print(user_form.errors, profile_form.errors)
    else:
        # a HTTP GET, render form using two ModelForm instance.
        user_form = UserForm()
        profile_form = UserProfileForm()


    # render the template depending on the context.
    return render(request, 'rango/register.html',
                 {'user_form': user_form,
                  'profile_form': profile_form,
                  'registered': registered})
"""

"""
def user_login(request):
    # if a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':
        # get('username') can return Non, request.POST['username'] will raise 
        # KeyError exception.
        username = request.POST.get('username')
        password = request.POST.get('password')

        # if username/pw combination is valid then reture a user object.
        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                # the account is valid and active.
                login(request, user)
                return HttpResponseRedirect(reverse('index'))
            else:
                # an inactive account
                return HttpResponse("Your rango account is disabled.")
        # Bad login details were provided.
        else:
            print("Invalid login details: {0}, {1}".format(username, password))
            return HttpResponse("Invalid login details supplied.")
    # a HTTP GET.
    else:
        return render(request, 'rango/login.html', {})
"""


@login_required
def restricted(request):
    return render(request, 'rango/restricted.html', {})
    #return HttpResponse("Since you are logind in, you can see this text.")

"""
@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))
"""


# A helper method
def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val


def visitor_cookie_handler(request):
    # get('visits', '1'), the default value is 1.
    visits = int(get_server_side_cookie(request, 'visits', '1'))

    last_visit_cookie = get_server_side_cookie(request, 'last_visit', str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7], 
                                        '%Y-%m-%d %H:%M:%S')

    # if it's been more than a day since the last visit ....
    if (datetime.now() - last_visit_time).seconds > 10:
        visits = visits + 1
        # update the last visit cookie now that we have updated the count
        request.session['last_visit'] = str(datetime.now())
    else:
        visits = 1
        # set the last visit cookie
        request.session['last_visit'] = last_visit_cookie

    # update/set the visit cookie
    request.session['visits'] = visits


def search(request):
    result_list = []

    if request.method == 'POST':
        query = request.POST['query'].strip()
        if query:
            # run Bing search function to get the result list.
            result_list = run_query(query)

    return render(request, 'rango/search.html', {'result_list': result_list})


def track_url(request):
    # count page views
    page_id = None
    url = '/rango/'
    if request.method == 'GET':
        if 'page_id' in request.GET:
            page_id = request.GET['page_id']

            try:
                page = Page.objects.get(id=page_id)
                page.views = page.views + 1
                page.save()
                url = page.url
            except:
                pass

    return redirect(url)


@login_required
def register_profile(request):
    form = UserProfileForm()

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES)
        if form.is_valid():
            user_profile = form.save(commit=False)
            user_profile.user = request.user
            user_profile.save()

            return redirect('index')
        else:
            print(form.errors)

    context_dict = {'form': form}

    return render(request, 'rango/register_profile.html', context_dict)


@login_required
def profile(request, username):
    try:
        user = User.objects.get(username=username)
        print("***" + user.username)
    except User.DoesNotExist:
        return redirect('index')

    userprofile = UserProfile.objects.get_or_create(user=user)[0]
    print("***" + userprofile.website)

    form = UserProfileForm({'website': userprofile.website,
                            'picture': userprofile.picture})

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if form.is_valid():
            form.save(commit=True)
            return redirect('profile', user.username)
        else:
            print(form.errors)

    return render(request, 'rango/profile.html', 
            {'userprofile': userprofile, 'selecteduser': user, 'form': form})


@login_required
def list_profiles(request):
    userprofile_list = UserProfile.objects.all()

    return render(request, 'rango/list_profiles.html', 
                    {'userprofile_list': userprofile_list})


@login_required
def like_category(request):
    """ get category_id and increase category.likes, then return the likes."""
    cat_id = None
    if request.method == 'GET':
        cat_id = request.GET['category_id']
        likes = 0
        if cat_id:
            cat = Category.objects.get(id=int(cat_id))
            if cat:
                likes = cat.likes + 1
                cat.likes = likes
                cat.save()
    return HttpResponse(likes)


def get_category_list(max_results=0, starts_with=''):
    cat_list = []
    if starts_with:
        cat_list = Category.objects.filter(name__istartswith=starts_with)

    if max_results > 0:
        if len(cat_list) > max_results:
            cat_list = cat_list[:max_results]

    return cat_list


def suggest_category(request):
    print("enter***")
    cat_list = []
    starts_with = ''

    if request.method == 'GET':
        starts_with = request.GET['suggestion']
    cat_list = get_category_list(8, starts_with)

    return render(request, 'rango/cats.html', {'cats': cat_list})


