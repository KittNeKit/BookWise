# Generated by Django 4.2.3 on 2023-07-08 16:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('borrowings', '0005_payment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='to_pay',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
    ]