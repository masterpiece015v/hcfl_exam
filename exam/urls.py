"""hcfl_exam URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index , name='index'),
    path('new_user/',views.new_user,name='new_user'),
    path('select_menu/',views.select_menu,name='select_menu'),
    path('select_grade/<str:kind>',views.select_grade,name='select_grade'),
    path('question/',views.question,name='question'),
    path('question/<int:no>/<int:test_id>/<str:ans>/',views.question,name='question'),
    path('question_update/',views.question_update,name='question_update'),
    path('question_print/',views.question_print,name='question_print'),
    path('user_update/',views.user_update,name='user_update'),
]
