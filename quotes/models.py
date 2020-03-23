from django.db import models

# Create your models here.
from django.db import models
from datetime import datetime, date
import bcrypt
import re


# Create your models here.

class UserManager(models.Manager):
    def registration_validator(self, postData):
        errors = {}

        try:
            first_name = postData['reg_first_name']
            last_name = postData['reg_last_name']
            email = postData['reg_email']
            #birthday = postData['reg_birthday']
            password = postData['reg_password']
            confirm_password = postData['reg_confirm_password']

            if first_name.isalpha():
                if not 2 < len(first_name) <= 50:
                    print("first name length error")
                    errors['first_name_length'] = 'First Name has to be between 2 and 50 characters long'
            else:
                print("first name alpha only")
                errors['first_name_alpha'] = 'Letter only for First Name'

            if last_name.isalpha():
                if not 2 < len(last_name) <= 50:
                    errors['last_name_length'] = 'Last Name has to be between 2 and 50 characters long'
            else:
                errors['last_name_alpha'] = 'Letter only for Last Name'

            email_regex = re.compile("(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")

            if email_regex.search(email) is None:
                print("email is invalid")
                # if email is invalid
                errors['email'] = "Email is invalid"
            elif len(User.objects.filter(email=postData['reg_email'])) > 0:
                print("received a duplicate email")
                errors['email'] = "This email has been registered, please choose a different email"

            """"
            if birthday == "":
                errors['birthday'] = "Birthday can't be empty"
            elif datetime.strptime(birthday, "%Y-%m-%d") > datetime.now():
                errors['birthday'] = "Birthday can't be a future date"
            elif (date.today() - datetime.strptime(birthday, "%Y-%m-%d").date()).days / 365.2425 < 13:
                errors['birthday'] = "Needs to be at least 13 years old"
            """
            if len(password) < 8:
                errors['password_length'] = "Password has to be at least 8 characters"
                if password != confirm_password:
                    errors['password_confirm'] = "Password has to match password confirmation"
        except Exception as e:
            print(e)
            errors['exceptions'] = "unexpected errors happened in registration validator"

        return errors


class UserloginManager(models.Manager):
    def login_validator(self, postData):
        errors = {}

        try:
            login_email = postData['login_email']
            login_password = postData['login_password']

            if len(login_email) == 0 or len(login_password) == 0:
                if len(login_email) == 0:
                    errors['login_email_length'] = "Email can not be empty"
                if len(login_password) == 0:
                    errors['login_password_length'] = "Password can not be empty"
            else:
                user = User.objects.filter(email=login_email)
                #print(user.__dict__)
                # this return a result set (list)
                if user:
                    existed_user = user[0]
                    if not bcrypt.checkpw(login_password.encode(), existed_user.password.encode()):
                        errors['login_error'] = "Email and password doesn't match, can't log in"
                    else:
                        # success log in
                        pass
                else:
                    # no such user
                    errors['login_error'] = "No such user"
        except Exception as e:
            print(e)
            print("Unexpected error happened when running login validator")
            errors['login_validator_error'] = "Unexpected error happened when running login validator"

        return errors


class UserUpdateManager(models.Manager):
    def update_validator(self, postData, userID):
        errors = {}

        try:
            first_name = postData['edit_account_first_name']
            last_name = postData['edit_account_last_name']
            temp_new_email = postData['edit_account_email']
            orig_email = User.objects.filter(userId=userID)[0].email
            email_regex = re.compile("(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")

            if len(first_name) == 0 or len(last_name) == 0 or len(temp_new_email) == 0:
                errors['required_fields'] = "All fields must be filled"
            elif email_regex.search(temp_new_email) is None:
                print("email is invalid")
                # if email is invalid
                errors['email'] = "Email is invalid"
            elif len(User.objects.filter(email=temp_new_email)) > 0 and temp_new_email != orig_email:
                print("received a duplicate email")
                errors['email'] = "This email has been registered, please choose a different email"
        except Exception as e:
            print(e)
        return errors


class User(models.Model):
    userId = models.AutoField(primary_key=True)
    email = models.CharField(max_length=150)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    #birthday = models.DateField()
    password = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = UserManager()  # default manager
    login_validator = UserloginManager()
    update_validator = UserUpdateManager()



class QuoteManager(models.Manager):
    def create_validator(self, postData):
        errors = {}
        try:
            author = postData['add_quote_text_author']
            quote = postData['add_quote_textarea_quote']

            if len(author) < 4:
                errors['author_length'] = "Author has to be more than 3 characters"
            if len(quote) < 11:
                errors['quote_length'] = "Quote has to be more than 10 characters"

        except Exception as e:
            errors['error'] = "unexpected error in Quote validation"

        return errors

class Quote(models.Model):
    quoteId = models.AutoField(primary_key=True)
    author = models.CharField(max_length=100)
    quote = models.CharField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, related_name='quotes', on_delete=models.CASCADE)
    like = models.ManyToManyField(User, related_name='likes')
    objects = QuoteManager()



