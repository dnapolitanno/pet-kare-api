
from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView, Request, Response, status
from groups.models import Group
from traits.models import Trait
from .models import Pet
from .serializers import PetSerializer


class CustomPagination(PageNumberPagination):
    page_size = 2


class PetView(APIView):
    def get(self, request: Request) -> Response:
        pagination = CustomPagination()

        pets = Pet.objects.all()
        trait = request.query_params.get('trait')

        if trait:
            pets = pets.filter(traits__name=trait)

        result_page = pagination.paginate_queryset(pets, request)
        serializer = PetSerializer(result_page, many=True)

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


class PetDetailView(APIView):
    def get(self, request, pet_id):
        pet = get_object_or_404(Pet, id=pet_id)
        serializer = PetSerializer(pet)
        return Response(serializer.data)

    def delete(self, request, pet_id):
        pet = get_object_or_404(Pet, id=pet_id)
        pet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, pet_id):
        pet = get_object_or_404(Pet, id=pet_id)
        serializer = PetSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        group = serializer.validated_data.pop('group', None)
        traits = serializer.validated_data.pop('traits', None)

        if group:
            group_data = Group.objects.filter(
                scientific_name__iexact=group['scientific_name']
            ).first()

            if not group_data:
                group_data = Group.objects.create(**group)

            pet.group = group_data

        if traits:
            pet.traits.clear()
            for trait_dict in traits:
                trait_data = Trait.objects.filter(
                    name__iexact=trait_dict['name']
                ).first()

                if not trait_data:
                    trait_data = Trait.objects.create(**trait_dict)
                pet.traits.add(trait_data)

        for key, value in serializer.validated_data.items():
            setattr(pet, key, value)

        pet.save()
        serializer = PetSerializer(pet)

        return Response(serializer.data, status.HTTP_200_OK)
