from django.db import models
from django.core.validators import MinValueValidator


class Brand(models.Model):
	name = models.CharField('Marka adı', max_length=100, unique=True)

	class Meta:
		verbose_name = 'Marka'
		verbose_name_plural = 'Markalar'
		#ordering = ('name',)

	def __str__(self):
		return self.name


class ProductGroup(models.Model):
	name = models.CharField('Ürün grubu adı', max_length=150, unique=True)

	class Meta:
		verbose_name = 'Ürün grubu'
		verbose_name_plural = 'Ürün grupları'

	def __str__(self):
		return self.name


class Product(models.Model):
	photo = models.ImageField('Fotoğraf', upload_to='products/', blank=True)
	product_code = models.CharField('Ürün kodu', max_length=100, unique=True)
	product_group = models.ForeignKey(
		ProductGroup,
		verbose_name='Ürün grubu',
		on_delete=models.PROTECT,
		related_name='products',
	)
	name = models.CharField('Adı', max_length=200)
	technical_description = models.TextField('Teknik özellik açıklaması', blank=True)
	brand = models.ForeignKey(
		Brand,
		verbose_name='Marka',
		on_delete=models.PROTECT,
		related_name='products',
	)
	cost = models.DecimalField('Maliyet', max_digits=12, decimal_places=2)
	list_price = models.DecimalField('Liste satış fiyatı', max_digits=12, decimal_places=2)

	class Meta:
		verbose_name = 'Ürün'
		verbose_name_plural = 'Ürünler'
		#ordering = ('name',)

	def __str__(self):
		return self.product_code


class Stock(models.Model):
	product = models.OneToOneField(
		Product,
		verbose_name='Ürün',
		on_delete=models.CASCADE,
		related_name='stock',
	)
	quantity = models.PositiveIntegerField(
		'Stok sayısı',
		validators=[MinValueValidator(0)],
	)
	last_updated_at = models.DateTimeField('Son güncellenme tarihi', auto_now=True)

	class Meta:
		verbose_name = 'Stok'
		verbose_name_plural = 'Stoklar'
		#ordering = ('product__name',)

	def __str__(self):
		return f'{self.product} - {self.quantity}'

	def save(self, *args, **kwargs):
		if self.quantity == 0:
			if self.pk:
				self.delete()
			return
		super().save(*args, **kwargs)
