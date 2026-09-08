from django.db import models
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone

CITY_CHOICES = (
	('34', 'İstanbul'),
	('01', 'Adana'),
	('02', 'Adıyaman'),
	('03', 'Afyonkarahisar'),
	('04', 'Ağrı'),
	('68', 'Aksaray'),
	('05', 'Amasya'),
	('06', 'Ankara'),
	('07', 'Antalya'),
	('75', 'Ardahan'),
	('08', 'Artvin'),
	('09', 'Aydın'),
	('10', 'Balıkesir'),
	('74', 'Bartın'),
	('72', 'Batman'),
	('69', 'Bayburt'),
	('11', 'Bilecik'),
	('12', 'Bingöl'),
	('13', 'Bitlis'),
	('14', 'Bolu'),
	('15', 'Burdur'),
	('16', 'Bursa'),
	('17', 'Çanakkale'),
	('18', 'Çankırı'),
	('19', 'Çorum'),
	('20', 'Denizli'),
	('21', 'Diyarbakır'),
	('81', 'Düzce'),
	('22', 'Edirne'),
	('23', 'Elazığ'),
	('24', 'Erzincan'),
	('25', 'Erzurum'),
	('26', 'Eskişehir'),
	('27', 'Gaziantep'),
	('28', 'Giresun'),
	('29', 'Gümüşhane'),
	('30', 'Hakkari'),
	('31', 'Hatay'),
	('76', 'Iğdır'),
	('32', 'Isparta'),
	('35', 'İzmir'),
	('46', 'Kahramanmaraş'),
	('78', 'Karabük'),
	('70', 'Karaman'),
	('36', 'Kars'),
	('37', 'Kastamonu'),
	('38', 'Kayseri'),
	('79', 'Kilis'),
	('71', 'Kırıkkale'),
	('39', 'Kırklareli'),
	('40', 'Kırşehir'),
	('41', 'Kocaeli'),
	('42', 'Konya'),
	('43', 'Kütahya'),
	('44', 'Malatya'),
	('45', 'Manisa'),
	('47', 'Mardin'),
	('33', 'Mersin'),
	('48', 'Muğla'),
	('49', 'Muş'),
	('50', 'Nevşehir'),
	('51', 'Niğde'),
	('52', 'Ordu'),
	('80', 'Osmaniye'),
	('53', 'Rize'),
	('54', 'Sakarya'),
	('55', 'Samsun'),
	('63', 'Şanlıurfa'),
	('56', 'Siirt'),
	('57', 'Sinop'),
	('73', 'Şırnak'),
	('58', 'Sivas'),
	('59', 'Tekirdağ'),
	('60', 'Tokat'),
	('61', 'Trabzon'),
	('62', 'Tunceli'),
	('64', 'Uşak'),
	('65', 'Van'),
	('77', 'Yalova'),
	('66', 'Yozgat'),
	('67', 'Zonguldak'),
)

class Customer(models.Model):
	company_name = models.CharField('Firma adı', max_length=200)
	address = models.TextField('Firma adresi')
	email = models.EmailField('E-posta adresi')
	phone = models.CharField('Telefon numarası', max_length=30)
	city = models.CharField('Şehir', max_length=2, choices=CITY_CHOICES)
	offer_temporarily_closed = models.BooleanField(
		'Teklife geçici olarak kapalı',
		default=False,
	)
	discount_rate = models.DecimalField(
		'İskonto oranı (%)',
		max_digits=5,
		decimal_places=2,
		default=0,
		validators=[MinValueValidator(0), MaxValueValidator(100)],
	)
	responsible_personnel = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		verbose_name='Sorumlu personel',
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name='responsible_customers',
	)
	first_relationship_date = models.DateField(
		'İlk ilişki tarihi',
		default=timezone.localdate,
	)

	class Meta:
		verbose_name = 'Müşteri'
		verbose_name_plural = 'Müşteriler'

	def __str__(self):
		return self.company_name


class CustomerContact(models.Model):
	customer = models.ForeignKey(
		Customer,
		verbose_name='Müşteri',
		on_delete=models.CASCADE,
		related_name='contacts',
	)
	first_name = models.CharField('Adı', max_length=100)
	last_name = models.CharField('Soyadı', max_length=100)
	title = models.CharField('Ünvanı', max_length=150, blank=True)
	email = models.EmailField('E-posta adresi')
	phone = models.CharField('Telefon numarası', max_length=30)

	class Meta:
		verbose_name = 'Müşteri kişisi'
		verbose_name_plural = 'Müşteri kişileri'

	def __str__(self):
		return f'{self.first_name} {self.last_name}'