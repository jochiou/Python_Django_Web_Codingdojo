from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.showLoginRegTemplate), #done
    path('user/<int:userID>', views.showSingleUserQuotesTemplate), #done
    path('myaccount/<int:userID>', views.showUserAccountTemplate), #done
    path('myaccount/<int:userID>/edit', views.editUser), # done
    path('addQuote/<int:userID>', views.addQuoteByUserID), # done
    path('deleteQuote/<int:quoteID>', views.deleteQuoteByQuoteID), # done
    path('quotes', views.showQuotesDashboardTemplate), # missing likes
    path('register', views.register), # done
    path('login', views.login), # done
    path('logout', views.logout), # done
    path('likeOneQuote/<int:quoteID>', views.addLikeToQuote)

    #path('checkout/', views.processOrder)

]