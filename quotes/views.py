from django.shortcuts import render
from time import gmtime, strftime
from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages
from .models import User, Quote
import random
import bcrypt
# Create your views here.

def showLoginRegTemplate(request):
    return render(request, 'login_and_registration.html')


# get all quotes from db (GET)
def showQuotesDashboardTemplate(request):
    try:
        logged_in_userID = request.session['logged_in_user']
        if logged_in_userID is not None:
            #print("logged in user: {}".format(logged_in_userID))
            logged_in_user = User.objects.filter(userId=logged_in_userID)[0]
            firstname = logged_in_user.first_name
            lastname = logged_in_user.last_name

            #print("getting all quotes ... ")
            quotes = Quote.objects.all()

            #print("quotes count: {}".format(len(quotes)))
            #print(quotes)



            context = {
                'first_name': firstname,
                'last_name': lastname,
                'quotes': quotes
            }

            return render(request, 'quotes.html', context)
        else:
            print("not logged in, redirect to home page")
            return redirect("/")
    except Exception as e:
        print(e)
        #print("cant find variable: logged_in_user in session, redirect to home page")
        return redirect("/")

# form, add a quote to db (POST)
def addQuoteByUserID(request, userID):
    errors = {}
    errors = Quote.objects.create_validator(request.POST)

    author = request.POST['add_quote_text_author']
    quote = request.POST['add_quote_textarea_quote']

    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value, extra_tags=key)
    else:
        try:
            Quote.objects.create(
                author=author,
                quote=quote,
                user=User.objects.get(userId=userID)
            )
            print("add quote success")
        except Exception as e:
            print(e)

    return redirect("/quotes")

def showSingleUserQuotesTemplate(request, userID):

    if request.session['logged_in_user'] is not None:
        target_user = User.objects.filter(userId=userID)[0]
        quotes = Quote.objects.filter(user=target_user)
        context = {
            'first_name': target_user.first_name,
            'last_name': target_user.last_name,
            "quotes": quotes
        }
        print("success, reender single user template")
        return render(request, 'single_user_quotes_template.html', context)

    else:
        print("fail rediret to home")
        return redirect('/')


def showUserAccountTemplate(request, userID):
    try:
        if request.session['logged_in_user'] is not None:
            #print("Is logged in -- load user account tempolate")

            logged_in_userID = request.session['logged_in_user']
            logged_in_user = User.objects.filter(userId=logged_in_userID)[0]

            firstname = logged_in_user.first_name
            lastname = logged_in_user.last_name
            email = logged_in_user.email

            context = {
                'first_name': firstname,
                'last_name': lastname,
                'email': email
            }

            return render(request, 'edit_account_template.html', context)
        else:
            print("not logged in, redirect to home page")
            return redirect("/")
    except Exception as e:
        print(e)
        print("cant find variable: logged_in_user in session, redirect to home page")
        return redirect("/")

def deleteQuoteByQuoteID(request, quoteID):
    quoteToDelete = Quote.objects.get(quoteId=quoteID)
    quoteToDelete.delete()
    return redirect("/quotes")


def editUser(request, userID):
    errors = {}
    errors = User.update_validator.update_validator(request.POST, userID)

    if len(errors) > 0:
        print("update input error, doesn't touch db")
        for key, value in errors.items():
            messages.error(request, value, extra_tags=key)
        return redirect('/myaccount/{}'.format(request.session['logged_in_user']))
    else:
        try:
            user = User.objects.get(userId=userID)
            user.first_name = request.POST['edit_account_first_name']
            user.last_name = request.POST['edit_account_last_name']
            user.email = request.POST['edit_account_email']
            user.save()
            print("update success, redirect")

        except Exception as e:
            print(e)
            print("unexpected error happened during update (after input check)")
        return redirect('/myaccount/{}'.format(request.session['logged_in_user']))

def addLikeToQuote(request, quoteID):
    this_quote = Quote.objects.get(quoteId=quoteID)
    this_user = User.objects.get(userId=request.session['logged_in_user'])
    print("this quote: {}".format(this_quote.__dict__))
    print("the value of this quote's like: {}".format(this_quote.like.all()))
    this_quote.like.add(this_user)
    print("the value of this quote's like: {}".format(this_quote.like.all().count()))
    this_quote.save()
    return redirect("/quotes")


def login(request):
    errors = {}
    email = request.POST['login_email']
    password = request.POST['login_password']

    errors = User.login_validator.login_validator(request.POST)

    if len(errors) > 0:
        print("Login input error, didn't try to login")
        print("errors dict:" + str(errors))
        for key, value in errors.items():
            messages.error(request, value, extra_tags=key)
        return redirect("/")
    else:
        userid = User.objects.filter(email=email)[0].userId
        print('login success')
        request.session['logged_in_user'] = userid
        return redirect('/quotes')


def logout(request):
    request.session["logged_in_user"] = None
    return redirect("/")


def register(request):
    first_name = request.POST['reg_first_name']
    last_name = request.POST['reg_last_name']
    email = request.POST['reg_email']
    password = request.POST['reg_password']
    confirm_password = request.POST['reg_confirm_password']
    #birthday = request.POST['reg_birthday']

    errors = User.objects.registration_validator(request.POST)

    if len(errors) > 0:
        print("registration input error, doesnt touch db")
        print("errors dict:" + str(errors))
        for key, value in errors.items():
            messages.error(request, value, extra_tags=key)
        return redirect("/")

    else:
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode(), salt).decode()
        print("Hashed password: {}\nSalt: {}\nSalt (decode): {}".format(hashed_password, salt, salt.decode()))
        try:
            User.objects.create(
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=hashed_password,
                #birthday=birthday

            )
            # since we auto login the user upon successful account creation
            # we add user's id into session after account creation
            userId = User.objects.filter(email=email)[0].userId
            request.session['logged_in_user'] = userId

            return redirect("/quotes")

        except Exception as e:
            print(e)
            request.session['error_msg'] = "something went wrong during account registration"
            return redirect('/')

