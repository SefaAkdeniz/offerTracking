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


def offer_pdf_response(offer):
	from reportlab.lib import colors
	from reportlab.lib.pagesizes import A4
	from reportlab.lib.styles import getSampleStyleSheet
	from reportlab.lib.units import mm
	from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

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
	rows = [['Ürün', 'Marka', 'Adet', 'Birim fiyat', 'Tutar']]
	subtotal = Decimal('0')
	for item in items:
		amount = item.product.list_price * item.quantity
		subtotal += amount
		rows.append([
			item.product.name,
			item.product.brand.name,
			str(item.quantity),
			f'{item.product.list_price:,.2f} TL',
			f'{amount:,.2f} TL',
		])

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
		table = Table(rows, repeatRows=1, colWidths=[55 * mm, 32 * mm, 16 * mm, 28 * mm, 28 * mm])
		table.setStyle(TableStyle([
			('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
			('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
			('FONTNAME', (0, 0), (-1, -1), font_name),
			('GRID', (0, 0), (-1, -1), 0.35, colors.HexColor('#d1d5db')),
			('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f9fafb')),
			('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
			('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
			('TOPPADDING', (0, 0), (-1, -1), 6),
			('BOTTOMPADDING', (0, 0), (-1, -1), 6),
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
	response['Content-Disposition'] = f'attachment; filename="teklif-{offer.pk}-revizyon-{offer.revision_number}.pdf"'
	return response


@staff_member_required
def offer_pdf(request, offer_id):
	offer = get_object_or_404(
		Offer.objects.select_related('customer', 'created_by'),
		pk=offer_id,
	)
	return offer_pdf_response(offer)

# Create your views here.
