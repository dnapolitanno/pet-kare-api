
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView, Request, Response, status
from groups.models import Group
from traits.models import Trait
from .models import Pet
from .serializers import PetSerializer


class CustomPagination(PageNumberPagination):
    page_size = 2


class PetView(APIView):

    def get(self, request):
        pagination = CustomPagination()

        pets = Pet.objects.all()
        paginated_pets = pagination.paginate_queryset(pets, request)

        serializer = PetSerializer(instance=paginated_pets, many=True)

        return pagination.get_paginated_response(serializer.data)

    def post(self, request: Request) -> Response:
        serializer = PetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        group = serializer.validated_data.pop('group')
        traits = serializer.validated_data.pop('traits')

        group_data = Group.objects.filter(
            scientific_name__iexact=group['scientific_name']
        ).first()

        if not group_data:
            group_data = Group.objects.create(**group)

        pet_data = Pet.objects.create(**serializer.validated_data, group=group_data)

        for trait in traits:
            trait_data = Trait.objects.filter(name__iexact=trait['name']).first()

            if not trait_data:
                trait_data = Trait.objects.create(**trait)

            pet_data.traits.add(trait_data)

        serializer = PetSerializer(pet_data)

        return Response(serializer.data, status.HTTP_201_CREATED)
