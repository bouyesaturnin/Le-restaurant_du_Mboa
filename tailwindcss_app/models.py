from django.db import models
from django.contrib.auth.models import User

class Reservation(models.Model):
    nom = models.CharField(max_length=100)
    email = models.EmailField()
    telephone = models.CharField(max_length=20)
    date = models.DateField()
    heure = models.TimeField()
    personnes = models.PositiveIntegerField()
    message = models.TextField(blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Réservation de {self.nom} le {self.date} à {self.heure}"

from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=50)
    
    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"


    def __str__(self):
        return self.name

class Dish(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='dishes')
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    image = models.ImageField(upload_to='dishes/')
    
    class Meta:
        verbose_name = "Plat"
        verbose_name_plural = "Plats"

    def __str__(self):
        return self.name
    
class ContactMessage(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self): 
        return f"{self.name} - {self.subject}"
    


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)
    
    def total(self):
        return sum(item.total_price() for item in self.items.all())

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    def total_price(self):
        return self.dish.price * self.quantity