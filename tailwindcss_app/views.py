from django.shortcuts import render
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ReservationForm
from .models import ContactMessage
from django.shortcuts import render, redirect, get_object_or_404
from .models import Dish, Category, Order, OrderItem
import stripe
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.conf import settings
import stripe




# Create your views here.
def home(request):
    return render(request, 'home.html')


def reservation_view(request):
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save()

            # --- Email client (ASCII uniquement) ---
            sujet_client = "Confirmation de votre reservation - Le Gourmet"
            message_client = (
                f"Bonjour {reservation.nom},\n\n"
                "Merci pour votre reservation chez Le Gourmet !\n\n"
                "Voici les details de votre reservation :\n"
                f"- Date : {reservation.date.strftime('%d/%m/%Y')}\n"
                f"- Heure : {reservation.heure.strftime('%H:%M')}\n"
                f"- Nombre de personnes : {reservation.personnes}\n\n"
                "Nous avons bien pris en compte votre demande.\n"
                "A tres bientot !\n\n"
                "L'equipe du restaurant Le Gourmet"
            )

            send_mail(
                sujet_client,
                message_client,
                settings.DEFAULT_FROM_EMAIL,
                [reservation.email],
                fail_silently=False,
            )

            # --- Email restaurant (ASCII uniquement) ---
            sujet_resto = f"Nouvelle reservation de {reservation.nom}"
            message_resto = (
                "Une nouvelle reservation vient d'etre faite :\n\n"
                f"Nom : {reservation.nom}\n"
                f"E-mail : {reservation.email}\n"
                f"Telephone : {reservation.telephone}\n"
                f"Date : {reservation.date.strftime('%d/%m/%Y')}\n"
                f"Heure : {reservation.heure.strftime('%H:%M')}\n"
                f"Personnes : {reservation.personnes}\n"
                f"Message : {reservation.message or '-'}\n\n"
                "Pensez a confirmer la table !"
            )

            send_mail(
                sujet_resto,
                message_resto,
                settings.DEFAULT_FROM_EMAIL,
                [settings.RESTAURANT_EMAIL],
                fail_silently=False,
            )

            messages.success(
                request,
                "Votre reservation a bien ete enregistree. Un e-mail de confirmation vous a ete envoye."
            )
            return redirect('reservation')

    else:
        form = ReservationForm()

    return render(request, 'reservation.html', {'form': form})



def menu_view(request):
    categories = Category.objects.prefetch_related('dishes').all()
    return render(request, 'menu.html', {'categories': categories})


def about(request):
    return render(request, 'about.html')



def contact(request):

    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        subject = request.POST.get("subject")
        message = request.POST.get("message")

        ContactMessage.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message
        )

        return redirect("success")

    return render(request, "contact.html")


def add_to_cart(request, dish_id):
    cart = request.session.get('cart', {})
    cart[str(dish_id)] = cart.get(str(dish_id), 0) + 1
    request.session['cart'] = cart
    messages.success(request, "Plat ajouté au panier avec success !")
    return redirect('menu')



# Menu page
def menu_view(request):
    if request.GET.get("clear_cart") == "1":
        request.session["cart"] = {}
    categories = Category.objects.prefetch_related('dishes').all()
    return render(request, 'menu.html', {'categories': categories})

# Panier


def add_to_cart(request, dish_id):
    cart = request.session.get('cart', {})

    # si 'cart' est une liste (ancienne version), on la convertit en dict
    if isinstance(cart, list):
        new_cart = {}
        for id in cart:
            new_cart[str(id)] = new_cart.get(str(id), 0) + 1
        cart = new_cart

    # Ajouter au panier
    cart[str(dish_id)] = cart.get(str(dish_id), 0) + 1

    request.session['cart'] = cart
    return redirect('cart')  # redirige vers le panier



def remove_from_cart(request, dish_id):
    """Supprimer un plat du panier"""
    cart = request.session.get('cart', {})
    if str(dish_id) in cart:
        del cart[str(dish_id)]
        request.session['cart'] = cart
    return redirect('cart')


def cart_view(request):
    cart = request.session.get('cart', {})

    # IDs des plats dans le panier
    dish_ids = cart.keys()
    dishes = Dish.objects.filter(id__in=dish_ids)

    items = []
    total = 0

    for dish in dishes:
        quantity = cart[str(dish.id)]
        item_total = dish.price * quantity
        total += item_total

        items.append({
            "dish": dish,
            "quantity": quantity,
            "item_total": item_total
        })

    return render(request, "cart.html", {"items": items, "total": total})



# Checkout simulé
def checkout(request):
    cart = request.session.get('cart', {})

    if not cart:
        return redirect('menu')

    dishes = Dish.objects.filter(id__in=cart.keys())

    cart_items = []
    total = 0

    for dish in dishes:
        quantity = cart[str(dish.id)]
        subtotal = dish.price * quantity
        total += subtotal

        cart_items.append({
            "dish": dish,
            "quantity": quantity,
            "subtotal": subtotal,
        })

    # Quand on clique sur "Payer maintenant", on NE valide PAS encore la commande.
    if request.method == "POST":
        return redirect("payment")  # ➜ Aller vers la page de paiement

    return render(request, "checkout.html", {
        "cart_items": cart_items,
        "total": total
    })


def checkout_success(request):
    # On vide le panier seulement après paiement confirmé
    request.session["cart"] = {}
    return render(request, "checkout_success.html")
# Success

def checkout_cancel(request):
    return render(request, "checkout_cancel.html")


def payement(request):
    cart = request.session.get('cart', {})

    if not cart:
        return redirect('menu')

    # calcul du total
    total = 0
    dishes = Dish.objects.filter(id__in=cart.keys())
    for dish in dishes:
        total += dish.price * cart[str(dish.id)]

    # Si l'utilisateur confirme le paiement
    if request.method == "POST":
        request.session['cart'] = {}  # vider le panier
        return redirect('checkout_success')

    return render(request, "payement.html", {"total": total})



def create_checkout_session(request):
    cart = request.session.get("cart", {})

    if not cart:
        return redirect("menu")

    dishes = Dish.objects.filter(id__in=cart.keys())

    line_items = []
    for dish in dishes:
        quantity = cart[str(dish.id)]
        line_items.append({
            "price_data": {
                "currency": "eur",
                "unit_amount": int(dish.price * 100),  # prix en centimes
                "product_data": {"name": dish.name},
            },
            "quantity": quantity,
        })

    session = stripe.checkout.Session.create(
        mode="payment",
        payment_method_types=["card"],
        line_items=line_items,
        success_url=request.build_absolute_uri(reverse("checkout_success")),
        cancel_url=request.build_absolute_uri(reverse("checkout_cancel")),
    )

    return redirect(session.url)




# @csrf_exempt
# def stripe_webhook(request):
#     payload = request.body
#     sig_header = request.META["HTTP_STRIPE_SIGNATURE"]

#     try:
#         event = stripe.Webhook.construct_event(
#             payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
#         )
#     except Exception as e:
#         return HttpResponse(status=400)

#     if event["type"] == "checkout.session.completed":
#         session = event["data"]["object"]
#         print("PAIEMENT CONFIRMÉ :", session["id"])
#         # Ici : envoyer email, enregistrer commande, etc.

#     return HttpResponse(status=200)


def payer(request):
    if request.method == 'POST':
        stripe.api_key = settings.sk_test_51SUtDkJ0Oi3Jp8AVxaiu0kfiz4L03UhQC6FBoVg0cy1b64Dt51nSpGajcwiXTOq8SQ8dtGWQj2nG2Y7l171AzS5D00tpal8vkv
        token = request.POST['stripeToken']
        total = 0
        
        try:
            # Créer un client Stripe
            charge = stripe.Charge.create(
                amount=int(total * 100),  # Montant en centimes
                currency='eur',
                description='Paiement pour votre commande',
                source=token,
            )
            return redirect('success')  # Redirigez vers une page de succès
        except stripe.error.StripeError:
            return render(request, 'error.html')  # Gérer les erreurs

    return redirect('home')  # Redirigez vers la page d'accueil si la méthode n'est pas POST