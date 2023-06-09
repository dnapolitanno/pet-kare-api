from django.db import models


class Pet(models.Model):
    SEX_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('N', 'Not Informed'),
    ]

    name = models.CharField(max_length=50)
    age = models.IntegerField()
    weight = models.FloatField()
    sex = models.CharField(max_length=20, choices=SEX_CHOICES, default='N')

    group = models.ForeignKey(
        "groups.Group", on_delete=models.CASCADE, related_name="pet"
    )

    traits = models.ManyToManyField(
        'traits.Trait', related_name='pets'
        )

    def __repr__(self) -> str:
        return f"<Pet ({self.name} - ({self.age}))>"