from django.db import migrations, models
import django.db.models.deletion


def convert_product_groups(apps, schema_editor):
    Product = apps.get_model('product', 'Product')
    ProductGroup = apps.get_model('product', 'ProductGroup')

    for product in Product.objects.all():
        group, created = ProductGroup.objects.get_or_create(name=product.product_group)
        product.product_group_fk_id = group.pk
        product.save(update_fields=('product_group_fk',))


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0002_product_product_code_product_group'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, unique=True, verbose_name='Ürün grubu adı')),
            ],
            options={
                'verbose_name': 'Ürün grubu',
                'verbose_name_plural': 'Ürün grupları',
            },
        ),
        migrations.AddField(
            model_name='product',
            name='product_group_fk',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='products', to='product.productgroup', verbose_name='Ürün grubu'),
        ),
        migrations.RunPython(convert_product_groups, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='product',
            name='product_group',
        ),
        migrations.RenameField(
            model_name='product',
            old_name='product_group_fk',
            new_name='product_group',
        ),
        migrations.AlterField(
            model_name='product',
            name='product_group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='products', to='product.productgroup', verbose_name='Ürün grubu'),
        ),
    ]