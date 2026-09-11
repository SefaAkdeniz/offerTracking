from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone


class PaymentMethod(models.Model):
	name = models.CharField('Ödeme yöntemi', max_length=100)
	

	class Meta:
		verbose_name = 'Ödeme yöntemi'
		verbose_name_plural = 'Ödeme yöntemleri'

	def __str__(self):
		return self.name


class Offer(models.Model):
	class Status(models.TextChoices):
		DRAFT = 'draft', 'Taslak'
		SENT = 'sent', 'Gönderildi'
		APPROVED = 'approved', 'Onaylandı'
		REJECTED = 'rejected', 'Reddedildi'

	customer = models.ForeignKey(
		'customer.Customer',
		verbose_name='Müşteri',
		on_delete=models.PROTECT,
		related_name='offers',
	)
	customer_contact = models.ForeignKey(
		'customer.CustomerContact',
		verbose_name='Müşteri iletişim kişisi',
		on_delete=models.PROTECT,
		null=True,
		blank=True,
		related_name='offers',
	)
	offer_date = models.DateField('Teklif tarihi', default=timezone.localdate)
	status = models.CharField(
		'Teklif durumu',
		max_length=20,
		choices=Status.choices,
		default=Status.DRAFT,
	)
	payment_method = models.ForeignKey(
		PaymentMethod,
		verbose_name='Ödeme yöntemi',
		on_delete=models.PROTECT,
		null=True,
		blank=True,
		related_name='offers',
	)
	revision_number = models.PositiveIntegerField('Revizyon numarası', default=0, editable=False)
	created_by = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		verbose_name='Teklifi oluşturan kullanıcı',
		on_delete=models.SET_NULL,
		null=True,
		editable=False,
		related_name='created_offers',
	)
	discount = models.DecimalField(
		'Genel iskonto tutarı',
		max_digits=12,
		decimal_places=2,
		default=0,
		validators=[MinValueValidator(0)],
	)

	class Meta:
		verbose_name = 'Teklif'
		verbose_name_plural = 'Teklifler'

	def __str__(self):
		return f'{self.customer} - Teklif {self.pk or "Yeni"}'

	def clean(self):
		if self.customer and self.customer.offer_temporarily_closed:
			raise ValidationError({'customer': 'Bu müşteri için geçici olarak teklif oluşturulamaz.'})

		if self.customer_contact and self.customer_id != self.customer_contact.customer_id:
			raise ValidationError({'customer_contact': 'Müşteri kişisi seçilen müşteriye ait olmalıdır.'})

	@property
	def offer_number(self):
		creator = (self.created_by.username if self.created_by else 'kullanici-yok')[:3].upper()
		offer_number = f'{self.offer_date:%y}{creator}{self.pk}'
		if self.revision_number:
			offer_number += f'/{self.revision_number}'
		return offer_number

	@property
	def subtotal(self):
		return sum((item.total for item in self.items.all()), 0)

	@property
	def total(self):
		return max(self.subtotal - self.discount, 0)

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
	discount_rate = models.DecimalField(
		'İskonto oranı (%)',
		max_digits=5,
		decimal_places=2,
		default=0,
		validators=[MinValueValidator(0), MaxValueValidator(100)],
	)

	@property
	def subtotal(self):
		return self.product.list_price * self.quantity

	@property
	def discount_amount(self):
		return self.subtotal * self.discount_rate / 100

	@property
	def total(self):
		return self.subtotal - self.discount_amount

	class Meta:
		verbose_name = 'Teklif ürünü'
		verbose_name_plural = 'Teklif ürünleri'
		constraints = [
			models.UniqueConstraint(fields=('offer', 'product', 'discount_rate'), name='unique_offer_product'),
		]

	def __str__(self):
		return f'{self.product} - {self.quantity} Adet'