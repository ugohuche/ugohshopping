from django.conf import settings
from django.db import migrations, models
from django_countries.fields import CountryField
import django.db.models.deletion


class Migration(migrations.Migration):
  
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(choices=[('S', 'Shirt'), ('SW', 'Sports wear'), ('OW', 'Outwear')], max_length=2)),
                ('label', models.CharField(choices=[('P', 'primary'), ('S', 'secondary'), ('D', 'danger')], max_length=2)),
                ('title', models.CharField(max_length=100)),
                ('price', models.FloatField()),
                ('discount_price', models.FloatField(blank=True, null=True)),
                ('image', models.ImageField()),
                ('slug', models.SlugField()),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ordered', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Item')), 
            ],
        ),
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('default', models.BooleanField(default=False)),
                ('apartment_address', models.CharField(blank=True, max_length=100, null=True)),
                ('address_type', models.CharField(choices=[('B', 'Billing'), ('S', 'Shipping')], max_length=1)),
                ('Zip', models.CharField(max_length=100)),
                ('street_address', models.CharField(max_length=100)),
                ('country', CountryField(multiple=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('being_delivered', models.BooleanField(default=False)),
                ('ordered', models.BooleanField(default=False)),
                ('recieved', models.BooleanField(default=False)),
                ('refund_granted', models.BooleanField(default=False)),
                ('refund_requested', models.BooleanField(default=False)),
                ('reference_code', models.CharField(blank=True, max_length=20, null=True)),
                ('ordered_date', models.DateTimeField()),
                ('start_date', models.DateTimeField(auto_now_add=True)),
                ('billing_address', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.SET_NULL, null=True, related_name='billing_address', to='core.Address')),
                ('shipping_address', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.SET_NULL, null=True, related_name='shipping_address', to='core.Address')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('items', models.ManyToManyField(to='core.OrderItem')),
            ],
        ),
        migrations.CreateModel(
            name='Refund',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('accepted', models.BooleanField(default=False)),
                ('email', models.EmailField()),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Order')),
                ('reason', models.TextField()),
            ],
        ),
    ]