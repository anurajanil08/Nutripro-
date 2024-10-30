from django.urls import path
from accounts import views


app_name = "accounts"

urlpatterns = [
  path("",views.index,name="index"),
  path("shoppage/",views.shop_page,name="shop_page"),
  path("about",views.about,name="about"),


]