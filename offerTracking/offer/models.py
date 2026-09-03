from django.db import models
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone


class Offer(models.Model):
	customer = models.ForeignKey(
		'customer.Customer',
		verbose_name='Müşteri',
		on_delete=models.PROTECT,
		related_name='offers',
	)
	offer_date = models.DateField('Teklif tarihi', default=timezone.localdate)
	revision_number = models.PositiveIntegerField('Revizyon numarası', default=1, editable=False)
	created_by = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		verbose_name='Teklifi oluşturan kullanıcı',
		on_delete=models.SET_NULL,
		null=True,
		editable=False,
		related_name='created_offers',
	)
	discount_rate = models.DecimalField(
		'İskonto oranı (%)',
		max_digits=5,
		decimal_places=2,
		blank=True,
		null=True,
		validators=[MinValueValidator(0), MaxValueValidator(100)],
	)

	class Meta:
		verbose_name = 'Teklif'
		verbose_name_plural = 'Teklifler'
		#ordering = ('-offer_date', '-id')

	def __str__(self):
		return f'{self.customer} - Teklif {self.pk or "yeni"} - Revizyon {self.revision_number}'

	def save(self, *args, **kwargs):
		if self.pk:
			self.revision_number += 1
		super().save(*args, **kwargs)


class OfferItem(models.Model):
	offer = models.ForeignKey(
		Offer,
		verbose_name='Teklif',
		on_delete=models.CASCADE,
		related_name='items',
	)
	product = models.ForeignKey(
		'product.Product',
		verbose_name='Ürün',
		on_delete=models.PROTECT,
		related_name='offer_items',
	)
	quantity = models.PositiveIntegerField(
		'Adet',
		validators=[MinValueValidator(1)],
	)

	class Meta:
		verbose_name = 'Teklif ürünü'
		verbose_name_plural = 'Teklif ürünleri'
		constraints = [
			models.UniqueConstraint(fields=('offer', 'product'), name='unique_offer_product'),
		]

	def __str__(self):
		return f'{self.product} - {self.quantity}'
