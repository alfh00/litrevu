import random

from django.core.management.base import BaseCommand
from faker import Faker
from PIL import Image

from authentication.models import User
from feed.models import Photo, Review, Ticket

fake = Faker()


class Command(BaseCommand):
    help = "Generate fake data for your app"

    def handle(self, *args, **options):
        num_users = 10  # Adjust these values as needed
        num_photos = 10
        num_tickets = 10
        num_reviews_per_ticket = 3
        num_user_follows = 5

        users = User.objects.all()
        photos = Photo.objects.all()

        # Generate and save fake User objects
        for i in range(num_users):
            username = fake.user_name()
            email = fake.email()
            profile_photo = fake.image_url()

            user = User(
                username=username,
                email=f"email{i}@email.fr",
                profile_photo=profile_photo,
            )
            user.set_password("S3cret!!!")  # Set a default password for users
            user.save()

        # Generate and save fake Photo, Ticket, Review objects, and UserFollows relationships
        for _ in range(num_photos):
            files = ["1.jpg", "2.jpg", "3.jpg"]
            caption = fake.sentence(nb_words=6)
            uploader = fake.random_element(users)  # Get a random user as the uploader

            photo = Photo(
                file=random.choice(files),
                caption=caption,
                uploader=uploader,
            )
            photo.save()

        for _ in range(num_tickets):
            title = fake.sentence(nb_words=4)
            description = fake.paragraph(nb_sentences=3)
            user = fake.random_element(users)  # Get a random user
            photo = fake.random_element(photos)  # Get a random user

            ticket = Ticket(
                title=title,
                description=description,
                user=user,
                image=photo,
            )
            ticket.save()

            for _ in range(num_reviews_per_ticket):
                rating = fake.random_int(min=1, max=5)
                headline = fake.sentence(nb_words=4)
                body = fake.paragraph(nb_sentences=3)
                user = fake.random_element(users)  # Get a random user

                review = Review(
                    ticket=ticket,
                    rating=rating,
                    user=user,
                    headline=headline,
                    body=body,
                )
                review.save()

            users = list(User.objects.all())  # Convert queryset to a list

            # Generate and save fake UserFollows relationships
            for _ in range(num_user_follows):
                user = fake.random_element(users)
                followed_user = fake.random_element(users)

                # Ensure that the user is not following themselves
                while followed_user == user:
                    followed_user = fake.random_element(users)

                # Create UserFollows relationship
                user.follows.add(followed_user)

        self.stdout.write(self.style.SUCCESS("Successfully generated fake data."))
