# Generated by Django 5.1.4 on 2025-01-03 14:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('borrowing_service', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('PAID', 'Paid')], default='PENDING', max_length=7)),
                ('type', models.CharField(choices=[('PAYMENT', 'Payment'), ('FINE', 'Fine')], default='FINE', max_length=7)),
                ('session_url', models.URLField()),
                ('session_id', models.CharField(max_length=7)),
                ('money_to_pay', models.DecimalField(decimal_places=2, max_digits=10)),
                ('borrowing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='borrowing_service.borrowing')),
            ],
        ),
    ]
