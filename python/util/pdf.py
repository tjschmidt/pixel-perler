from io import BytesIO
from math import ceil
from typing import List, Dict, Iterable

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, PageBreak, Flowable, Paragraph

from pixel.settings import PDF_TEXT

_STYLES = getSampleStyleSheet()
_CELL_SIZE = [5 * mm]

VALID_COLOR_CODES = [chr(char_val) for char_val in range(ord('0'), ord('9'))] + \
                    [chr(char_val) for char_val in range(ord('A'), ord('Z')) if char_val != ord('I')] + \
                    [chr(char_val) for char_val in range(ord('a'), ord('z')) if char_val != ord('l')]


class PDFGenerator:
    def __init__(self, color_map: Dict[str, str], data: List[str], total_width: int, num_cols: int = 30,
                 text: Iterable[str] = None):
        """
        Constructor
        :param color_map: dict of color_code -> color_name
        :param data: list of color codes (row-major ordering)
        :param total_width: width of the output image
        :param num_cols: maximum number of columns per page
        :param text: strings to add to the cover page
        :return: bytes of the generated PDF
        """
        self._color_map = color_map
        self._data = data
        self._total_width = total_width
        self._num_cols = num_cols
        self._text = text
        self._code_remap = {}

    def generate_pdf(self) -> bytes:
        """
        Generates a PDF of the color data provided
        """
        # Initialize components with cover page
        components = [*self._generate_cover_page(self._color_map, self._data, paragraphs=self._text), PageBreak()]

        # Calculate number of pages (width)
        num_sections = int(ceil(self._total_width / self._num_cols))

        for section in range(num_sections):

            # Extract columns for this page
            start_col = section * self._num_cols
            section_cols = min(self._num_cols, self._total_width - start_col)
            end_col = start_col + section_cols

            # Extract rows for this page
            rows = [[self._code_remap[self._data[i + self._total_width * j]] for i in range(start_col, end_col)]
                    for j in range(int(ceil(len(self._data) / self._total_width)))]

            # Create table
            table = Table(rows, colWidths=_CELL_SIZE * len(rows[0]), rowHeights=_CELL_SIZE * len(rows))
            style = TableStyle([
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.lightgrey])
            ])
            table.setStyle(style)
            components.append(table)

            # Insert page break if applicable
            if section < num_sections - 1:
                components.append(PageBreak())

        # Build the document
        with BytesIO() as buffer:
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            # doc.build(components, onFirstPage=_header, onLaterPages=_header)
            doc.build(components)
            return buffer.getvalue()

    def _generate_cover_page(self, color_map: Dict[str, str], data: List[str], paragraphs: Iterable[str] = None) -> \
            List[Flowable]:
        """
        Generate the cover page for the PDF
        :param color_map: dict of color_code -> color_name
        :param data: list of color codes (column-major ordering)
        :param paragraphs: paragraphs to add to the cover page
        :return: PDF Flowable containing the relevant data
        """
        flowables = []

        # Include introductory paragraphs
        if paragraphs is not None:
            for paragraph in paragraphs:
                flowables.append(Paragraph(paragraph, style=_STYLES['Normal']))
                flowables.append(Paragraph('<br/><br/>', style=_STYLES['Normal']))

        # Count occurrences of each color
        counts = {}
        for item in data:
            counts[item] = counts.get(item, 0) + 1
        sorted_counts = sorted([(color_code, count) for (color_code, count) in counts.items() if count > 0],
                               key=lambda tup: tup[1],
                               reverse=True)

        # Remap the color codes so that the PDF is more intuitive
        # This will force the use of 0-9, then A-Z, etc. rather than skipping around
        self._code_remap = {code: VALID_COLOR_CODES[i] for (i, code) in enumerate(tup[0] for tup in sorted_counts)}

        # Organize color codes into a table
        row_data = [['Color Code', 'Color Name', 'Number of Beads']]
        row_data += [[self._code_remap[tup[0]], color_map[tup[0]], tup[1]] for tup in sorted_counts]

        # Create table
        table = Table(row_data)
        table_style = TableStyle([
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.lightgrey])
        ])
        table.setStyle(table_style)
        table_description = 'The table below contains the color codes that you will find in the grid, along with the ' \
                            'number of each color required.'
        flowables.append(Paragraph(table_description + '<br/><br/>', style=_STYLES['Normal']))
        flowables.append(table)

        return flowables

    @staticmethod
    def _header(canvas, doc) -> None:
        """
        Add a header to the page
        """
        canvas.drawCentredString(doc.width / 2, doc.height - doc.topMargin / 2, PDF_TEXT['HEADER'])
