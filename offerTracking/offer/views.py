from decimal import Decimal
from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape

from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from .models import Offer


def _register_pdf_font():
	from reportlab.pdfbase import pdfmetrics
	from reportlab.pdfbase.ttfonts import TTFont

	font_paths = (
		Path('C:/Windows/Fonts/arial.ttf'),
		Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'),
	)
	for font_path in font_paths:
		if font_path.exists():
			pdfmetrics.registerFont(TTFont('OfferFont', str(font_path)))
			return 'OfferFont'
	return 'Helvetica'


def offer_pdf_response(offer, include_photos=True):
	from reportlab.lib import colors
	from reportlab.lib.pagesizes import A4
	from reportlab.lib.styles import getSampleStyleSheet
	from reportlab.lib.enums import TA_RIGHT
	from reportlab.lib.units import mm
	from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

	buffer = BytesIO()
	document = SimpleDocTemplate(
		buffer,
		pagesize=A4,
		rightMargin=18 * mm,
		leftMargin=18 * mm,
		topMargin=18 * mm,
		bottomMargin=18 * mm,
	)
	font_name = _register_pdf_font()
	styles = getSampleStyleSheet()
	styles['Normal'].fontName = font_name
	styles['Title'].fontName = font_name
	styles['Heading2'].fontName = font_name

	items = list(offer.items.select_related('product__brand'))
	cell_style = styles['Normal'].clone('OfferCell')
	cell_style.fontName = font_name
	cell_style.fontSize = 8
	cell_style.leading = 10
	numeric_style = cell_style.clone('OfferNumericCell')
	numeric_style.alignment = TA_RIGHT
	numeric_style.fontSize = 7
	numeric_style.leading = 9
	header_style = cell_style.clone('OfferHeaderCell')
	header_style.fontName = font_name
	header_style.fontSize = 7
	header_style.leading = 8
	if include_photos:
		rows = [[Paragraph(header, header_style) for header in ('Fotoğraf', 'Ürün', 'Marka', 'Teknik özellikler', 'Adet', 'Birim fiyat', 'Tutar')]]
	else:
		rows = [[Paragraph(header, header_style) for header in ('Ürün', 'Marka', 'Teknik özellikler', 'Adet', 'Birim fiyat', 'Tutar')]]
	subtotal = Decimal('0')
	for item in items:
		amount = item.product.list_price * item.quantity
		subtotal += amount
		item_rows = [
			Paragraph(escape(item.product.name), cell_style),
			Paragraph(escape(item.product.brand.name), cell_style),
			Paragraph(escape(item.product.technical_description or '-').replace('\n', '<br/>'), cell_style),
			Paragraph(str(item.quantity), numeric_style),
			Paragraph(f'{item.product.list_price:,.2f} TL', numeric_style),
			Paragraph(f'{amount:,.2f} TL', numeric_style),
		]
		if include_photos:
			if item.product.photo:
				photo = Image(item.product.photo.path, width=25 * mm, height=20 * mm, kind='proportional')
			else:
				photo = Paragraph('Fotoğraf yok', cell_style)
			item_rows.insert(0, photo)
		rows.append(item_rows)

	discount_rate = offer.discount_rate or Decimal('0')
	discount_amount = subtotal * discount_rate / Decimal('100')
	total = subtotal - discount_amount
	story = [
		Paragraph('TEKLİF', styles['Title']),
		Spacer(1, 6 * mm),
		Paragraph(f'<b>Müşteri:</b> {escape(offer.customer.company_name)}', styles['Normal']),
		Paragraph(f'<b>Teklif tarihi:</b> {offer.offer_date:%d.%m.%Y}', styles['Normal']),
		Paragraph(f'<b>Revizyon:</b> {offer.revision_number}', styles['Normal']),
		Paragraph(
			f'<b>Oluşturan:</b> {escape(offer.created_by.get_full_name() or offer.created_by.username) if offer.created_by else "-"}',
			styles['Normal'],
		),
		Spacer(1, 8 * mm),
	]
	if not items:
		story.append(Paragraph('Bu teklifte ürün bulunmamaktadır.', styles['Normal']))
	else:
		column_widths = (
			[25, 30, 22, 38, 12, 23, 24]
			if include_photos
			else [38, 25, 57, 12, 21, 21]
		)
		table = Table(rows, repeatRows=1, colWidths=[width * mm for width in column_widths])
		table.setStyle(TableStyle([
			('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
			('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
			('FONTNAME', (0, 0), (-1, -1), font_name),
			('GRID', (0, 0), (-1, -1), 0.35, colors.HexColor('#d1d5db')),
			('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f9fafb')),
			('ALIGN', (4 if include_photos else 3, 1), (-1, -1), 'RIGHT'),
			('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
			('TOPPADDING', (0, 0), (-1, -1), 4),
			('BOTTOMPADDING', (0, 0), (-1, -1), 4),
			('LEFTPADDING', (0, 0), (-1, -1), 4),
			('RIGHTPADDING', (0, 0), (-1, -1), 4),
		]))
		story.extend([table, Spacer(1, 8 * mm)])

	summary = [
		['Ara toplam:', f'{subtotal:,.2f} TL'],
		[f'İskonto (%{discount_rate:,.2f}):', f'-{discount_amount:,.2f} TL'],
		['Genel toplam:', f'{total:,.2f} TL'],
	]
	summary_table = Table(summary, colWidths=[45 * mm, 35 * mm], hAlign='RIGHT')
	summary_table.setStyle(TableStyle([
		('FONTNAME', (0, 0), (-1, -1), font_name),
		('ALIGN', (1, 0), (1, -1), 'RIGHT'),
		('LINEABOVE', (0, -1), (-1, -1), 1, colors.black),
		('FONTNAME', (0, -1), (-1, -1), font_name),
		('FONTSIZE', (0, -1), (-1, -1), 11),
	]))
	story.append(summary_table)
	document.build(story)
	response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
	photo_suffix = 'fotografli' if include_photos else 'fotografsiz'
	response['Content-Disposition'] = (
		f'attachment; filename="teklif-{offer.pk}-revizyon-{offer.revision_number}-{photo_suffix}.pdf"'
	)
	return response


@staff_member_required
def offer_pdf(request, offer_id):
	offer = get_object_or_404(
		Offer.objects.select_related('customer', 'created_by'),
		pk=offer_id,
	)
	include_photos = request.GET.get('photos', '1') != '0'
	return offer_pdf_response(offer, include_photos=include_photos)

# Create your views here.
