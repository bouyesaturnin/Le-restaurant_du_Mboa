from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from tailwindcss_app import views
from .views import menu_view
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('reservation/', views.reservation_view, name='reservation'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path("success/", lambda r: render(r, "success.html"), name="success"),
    path('cart/', views.cart_view, name='cart'),
    path('add-to-cart/<int:dish_id>/', views.add_to_cart, name='add_to_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('menu/', menu_view, name='menu'),
    path('remove-from-cart/<int:dish_id>/', views.remove_from_cart, name='remove_from_cart'),
    path("checkout/success/", views.checkout_success, name="checkout_success"),
    path("checkout/cancel/", views.checkout_cancel, name="checkout_cancel"),
    # path("stripe/webhook/", views.stripe_webhook, name="stripe_webhook"),
    path('payement/', views.payement, name='payement'),
    path('payer/', views.payer, name='payer'),
    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    