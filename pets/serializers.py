from rest_framework import serializers
from groups.serializers import GroupSerializer
from traits.serializers import TraitSerializer


class PetSerializer(serializers.Serializer):    
    SEX_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('N', 'Not Informed'),
    ]

    id = serializers.IntegerField(read_only=True)

    name = serializers.CharField(max_length=50)
    age = serializers.IntegerField()
    weight = serializers.FloatField()
    sex = serializers.ChoiceField(choices=SEX_CHOICES, default='N')

    group = GroupSerializer()
    traits = TraitSerializer(many=True)