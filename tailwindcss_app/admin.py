from django.contrib import admin
from .models import Reservation, Category, Dish
from .models import ContactMessage

# Register your models here.
@admin.register(Reservation)
class AdminPlat(admin.ModelAdmin):
    list_display = ('nom', 'email', 'telephone', 'date', 'heure', 'personnes', 'message')

@admin.register(Category)
class AdminCategory(admin.ModelAdmin):
     list_display = ["name"]


@admin.register(Dish)
class AdminDish(admin.ModelAdmin):
    list_display = ('category', 'name', 'description', 'price', 'image')


class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject", "created_at")
    list_filter = ("created_at",)
    search_fields = ("name", "email", "subject", "message")

admin.site.register(ContactMessage, ContactMessageAdmin)