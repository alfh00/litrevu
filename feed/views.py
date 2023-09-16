from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Avg, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, View

from authentication.models import User

from .forms import PhotoForm, Review, ReviewForm, TicketForm
from .models import Ticket

# Create your views here.


@login_required
def create_new_ticket(request):
    ticket_form = TicketForm()
    photo_form = PhotoForm()
    if request.method == "POST":
        ticket_form = TicketForm(request.POST)
        photo_form = PhotoForm(request.POST, request.FILES)
        # review_form = ReviewForm(request.POST)
        if any([ticket_form.is_valid(), photo_form.is_valid()]):
            photo = photo_form.save(commit=False)
            photo.uploader = request.user
            photo.save()
            ticket = ticket_form.save(commit=False)
            ticket.image = photo
            ticket.user = request.user
            ticket.save()
            return redirect(reverse("home"))
    forms = [ticket_form, photo_form]
    context = {
        "forms": forms,
    }
    return render(request, "feed/new_ticket.html", context=context)


@login_required
def create_new_ticket_review(request):
    ticket_form = TicketForm()
    photo_form = PhotoForm()
    review_form = ReviewForm()
    if request.method == "POST":
        ticket_form = TicketForm(request.POST)
        photo_form = PhotoForm(request.POST, request.FILES)
        review_form = ReviewForm(request.POST)
        if any([ticket_form.is_valid(), photo_form.is_valid(), review_form.is_valid()]):
            photo = photo_form.save(commit=False)
            photo.uploader = request.user
            photo.save()
            ticket = ticket_form.save(commit=False)
            ticket.image = photo
            ticket.user = request.user
            ticket.save()
            review = review_form.save(commit=False)
            review.ticket = ticket
            review.user = request.user
            review.save()
            return redirect(reverse("home"))
    forms = [ticket_form, photo_form, review_form]
    context = {
        "forms": forms,
    }
    return render(request, "feed/new_ticket.html", context=context)


@login_required
def get_all_tickets(request):
    tickets = Ticket.objects.filter(user=request.user)
    return render(request, "feed/all_tickets.html", context={"tickets": tickets})


@login_required
def get_single_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id)

    ticket.avg_rating = round(ticket.review_set.aggregate(avg_rating=Avg("rating"))["avg_rating"]) or 0
    ticket.review_count = ticket.review_set.count()

    return render(request, "feed/ticket_detail.html", {"ticket": ticket})


@login_required
def edit_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)

    if request.method == "POST":
        ticket_form = TicketForm(request.POST, instance=ticket)
        image_form = PhotoForm(request.POST, request.FILES, instance=ticket.image)

        if ticket_form.is_valid() and image_form.is_valid():
            ticket.image.delete()
            image = image_form.save(commit=False)
            image.uploader = request.user
            image.save()
            ticket = ticket_form.save(commit=False)
            ticket.image = image
            ticket.user = request.user
            ticket.save()
            return redirect("ticket_detail", ticket_id=ticket_id)
    else:
        ticket_form = TicketForm(instance=ticket)
        image_form = PhotoForm(instance=ticket.image)

    return render(
        request,
        "feed/edit_ticket.html",
        {"image_form": image_form, "ticket_form": ticket_form, "ticket": ticket},
    )


def delete_ticket(request, ticket_id):
    return DeleteView.as_view(
        model=Ticket,
        # Redirect to a success URL after deletion
        success_url=reverse_lazy("all_tickets"),
        template_name="feed/confirm_delete_ticket.html",  # Template for confirmation page
        context_object_name="ticket",  # Name to use for the ticket object in the template
        # Pass ticket_id to the template
        extra_context={"ticket_id": ticket_id},
    )(request, pk=ticket_id)


def add_review(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    ticket.avg_rating = round(ticket.review_set.aggregate(avg_rating=Avg("rating"))["avg_rating"])
    ticket.review_count = ticket.review_set.count()

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.ticket = ticket
            review.user = request.user
            review.save()
            messages.success(request, "Critique créé avec succes.")
            # Redirect to the ticket detail page
            return redirect("ticket_detail", ticket_id=ticket_id)
    else:
        form = ReviewForm()

    context = {
        "ticket": ticket,
        "form": form,
    }

    return render(request, "feed/add_review.html", context)


def edit_or_delete_review(request, ticket_id):
    # Get the ticket object
    ticket = get_object_or_404(Ticket, pk=ticket_id)

    # Find the user's review of this ticket
    user_review = Review.objects.filter(ticket=ticket, user=request.user).first()

    if not user_review:
        # User doesn't have a review for this ticket, redirect to the ticket detail page
        return redirect("ticket_detail", ticket_id=ticket_id)

    if request.method == "POST":
        form = ReviewForm(request.POST, instance=user_review)
        if "edit" in request.POST:  # Handle the "Edit" action
            if form.is_valid():
                form.save()
                messages.success(request, "Critique modifiée avec succes.")
                return redirect("home")
        elif "delete" in request.POST:
            return render(request, "feed/confirm_delete_review.html", {"user_review": user_review})
    else:
        form = ReviewForm(instance=user_review)

    context = {
        "ticket": ticket,
        "user_review": user_review,
        "form": form,
    }

    return render(request, "feed/edit_or_delete_review.html", context)


def delete_review(request, review_id):
    review = get_object_or_404(Review, pk=review_id)

    if review.user == request.user:
        review.delete()
        messages.success(request, "Critique supprimée avec succès.")
    else:
        messages.error(
            request,
            "Vous ne pouvez pas supprimer cette critique car vous n'en êtes pas le propriétaire.",
        )

    return redirect("home")


@login_required
def feed(request):
    current_user = request.user
    following_users = current_user.follows.all()

    tickets = (
        Ticket.objects.filter(user__in=following_users)
        .order_by("-time_created")
        .prefetch_related("review_set")
        .exclude(user=request.user)
    )

    for ticket in tickets:
        ticket.avg_rating = round(ticket.review_set.aggregate(avg_rating=Avg("rating"))["avg_rating"])
        ticket.review_count = ticket.review_set.count()
        ticket.already_reviewed = False
        for review in ticket.review_set.all():
            if review.user == request.user:
                ticket.already_reviewed = True
        # print()
        # print(ticket.avg_rating)
        # print(ticket.review_count)

    paginator = Paginator(tickets, per_page=1)
    page = request.GET.get("page")
    page_obj = paginator.get_page(page)
    context = {"page_obj": page_obj}
    return render(request, "feed/home.html", context)


@login_required
def discover(request):
    tickets = Ticket.objects.exclude(user=request.user)
    tickets = sorted(tickets, key=lambda instance: instance.time_created, reverse=True)
    paginator = Paginator(tickets, 6)
    page = request.GET.get("page")
    page_obj = paginator.get_page(page)

    context = {
        "page_obj": page_obj,
    }

    return render(request, "feed/discover.html", context)


@login_required
def following_followers_lists(request):
    # Get the search query from the URL parameter 'q'
    query = request.GET.get("q", "")
    users = []

    if query:
        users = User.objects.filter(username__icontains=query)

    # Get the currently logged-in user
    current_user = request.user

    # Retrieve the users that the current user is following
    following_users = current_user.follows.all()

    # Retrieve the users who are following the current user
    followers = User.objects.filter(follows=current_user)

    context = {
        "following_users": following_users,
        "followers": followers,
        "query": query,
        "users": users,
    }

    return render(request, "feed/following_followers_lists.html", context)


@login_required
def follow_user(request, user_id):
    user_to_follow = get_object_or_404(User, id=user_id)

    # Check if the user is not already following the user_to_follow
    if not request.user.follows.filter(id=user_id).exists():
        request.user.follows.add(user_to_follow)

    return redirect("following_followers_lists")


@login_required
def unfollow_user(request, user_id):
    user_to_unfollow = get_object_or_404(User, id=user_id)

    # Check if the user is following the user_to_unfollow
    if request.user.follows.filter(id=user_id).exists():
        request.user.follows.remove(user_to_unfollow)

    return redirect("following_followers_lists")


# from django.http import JsonResponse
# from django.db.models import Avg, Count
# from .models import Review

# def reviews_data(request):
#     # Get all reviews
#     reviews = Review.objects.all()

#     # Calculate average rating
#     average_rating = reviews.aggregate(avg_rating=Avg('rating'))

#     # Calculate review count
#     review_count = reviews.count()

#     # Create a dictionary to hold the data
#     data = {
#         'reviews': list(reviews.values()),  # Convert reviews queryset to a list of dictionaries
#         'average_rating': average_rating['avg_rating'],  # Get the average rating value
#         'review_count': review_count,  # Get the review count
#     }

#     return JsonResponse(data)
