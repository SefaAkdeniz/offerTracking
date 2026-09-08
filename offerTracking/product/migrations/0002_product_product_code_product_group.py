from django.db import migrations, models


def populate_product_fields(apps, schema_editor):
    Product = apps.get_model('product', 'Product')

    for product in Product.objects.filter(product_code__isnull=True):
        product.product_code = f'URUN-{product.pk}'
        product.product_group = 'Genel'
        product.save(update_fields=('product_code', 'product_group'))


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='product_code',
            field=models.CharField(max_length=100, null=True, verbose_name='Ürün kodu'),
        ),
        migrations.AddField(
            model_name='product',
            name='product_group',
            field=models.CharField(max_length=150, null=True, verbose_name='Ürün grubu'),
        ),
        migrations.RunPython(populate_product_fields, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='product',
            name='product_code',
            field=models.CharField(max_length=100, unique=True, verbose_name='Ürün kodu'),
        ),
        migrations.AlterField(
            model_name='product',
            name='product_group',
            field=models.CharField(max_length=150, verbose_name='Ürün grubu'),
        ),
    ]