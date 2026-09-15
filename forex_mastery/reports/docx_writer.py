"""
Minimal DOCX writer (standard library only).

A ``.docx`` file is just a ZIP archive of XML parts. Writing those parts
directly avoids a heavyweight dependency for what is, in this project, a
"make the handbook editable in Word" feature.

Supported: headings 1-4, paragraphs, bullet/numbered lists, tables, code blocks,
horizontal rules, and inline **bold** / *italic* / ``code``.

Not supported (deliberately): images, footnotes, custom styles, page numbering.
If you need those, open the generated file in Word/LibreOffice and save - the
document is valid OOXML and will round-trip.
"""

from __future__ import annotations

import re
import zipfile
from pathlib import Path

from .markdown_renderer import Block

__all__ = ["markdown_to_docx", "write_docx"]

_CONTENT_TYPES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
</Types>"""

_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""

_DOC_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>"""

_STYLES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:docDefaults>
    <w:rPrDefault><w:rPr>
      <w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:sz w:val="21"/>
    </w:rPr></w:rPrDefault>
  </w:docDefaults>
  <w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/>
    <w:pPr><w:spacing w:before="320" w:after="120"/><w:outlineLvl w:val="0"/></w:pPr>
    <w:rPr><w:b/><w:sz w:val="36"/><w:color w:val="1F3864"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/>
    <w:pPr><w:spacing w:before="260" w:after="100"/><w:outlineLvl w:val="1"/></w:pPr>
    <w:rPr><w:b/><w:sz w:val="28"/><w:color w:val="1F3864"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading3"><w:name w:val="heading 3"/>
    <w:pPr><w:spacing w:before="220" w:after="80"/><w:outlineLvl w:val="2"/></w:pPr>
    <w:rPr><w:b/><w:sz w:val="24"/><w:color w:val="2E5496"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading4"><w:name w:val="heading 4"/>
    <w:pPr><w:spacing w:before="180" w:after="60"/><w:outlineLvl w:val="3"/></w:pPr>
    <w:rPr><w:b/><w:i/><w:sz w:val="22"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Code"><w:name w:val="Code"/>
    <w:pPr><w:shd w:val="clear" w:fill="F2F2F2"/><w:spacing w:after="0"/></w:pPr>
    <w:rPr><w:rFonts w:ascii="Consolas" w:hAnsi="Consolas"/><w:sz w:val="18"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Quote"><w:name w:val="Quote"/>
    <w:pPr><w:ind w:left="360"/><w:pBdr><w:left w:val="single" w:sz="18" w:space="6" w:color="BFBFBF"/></w:pBdr></w:pPr>
    <w:rPr><w:i/></w:rPr></w:style>
</w:styles>"""


def _escape(text: str) -> str:
    return (
        text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    )


def _runs(text: str) -> str:
    """Convert inline markdown into OOXML runs."""
    out: list[str] = []
    pattern = re.compile(r"(\*\*.+?\*\*|\*[^*]+?\*|`[^`]+?`)", re.DOTALL)
    position = 0
    for match in pattern.finditer(text):
        if match.start() > position:
            out.append(_run(_escape(text[position:match.start()])))
        token = match.group(0)
        if token.startswith("**"):
            out.append(_run(_escape(token[2:-2]), bold=True))
        elif token.startswith("`"):
            out.append(_run(_escape(token[1:-1]), mono=True))
        else:
            out.append(_run(_escape(token[1:-1]), italic=True))
        position = match.end()
    if position < len(text):
        out.append(_run(_escape(text[position:])))
    return "".join(out) or _run("")


def _run(text: str, bold: bool = False, italic: bool = False, mono: bool = False) -> str:
    props = []
    if bold:
        props.append("<w:b/>")
    if italic:
        props.append("<w:i/>")
    if mono:
        props.append('<w:rFonts w:ascii="Consolas" w:hAnsi="Consolas"/>')
    rpr = f"<w:rPr>{''.join(props)}</w:rPr>" if props else ""
    return f"<w:r>{rpr}<w:t xml:space=\"preserve\">{text}</w:t></w:r>"


def _paragraph(text: str, style: str | None = None) -> str:
    ppr = f'<w:pPr><w:pStyle w:val="{style}"/></w:pPr>' if style else ""
    return f"<w:p>{ppr}{_runs(text)}</w:p>"


def _list_item(text: str, ordered: bool, index: int) -> str:
    prefix = f"{index}. " if ordered else "\u2022  "
    ppr = '<w:pPr><w:ind w:left="360" w:hanging="226"/></w:pPr>'
    return f"<w:p>{ppr}{_run(prefix)}{_runs(text)}</w:p>"


def _table(header: list[str], rows: list[list[str]]) -> str:
    def cell(text: str, bold: bool = False, width: int = 2400) -> str:
        return (
            f'<w:tc><w:tcPr><w:tcW w:w="{width}" w:type="dxa"/></w:tcPr>'
            f"<w:p>{_run(_escape(text), bold=bold)}</w:p></w:tc>"
        )

    borders = (
        '<w:tblBorders>'
        + "".join(
            f'<w:{edge} w:val="single" w:sz="6" w:space="0" w:color="BFBFBF"/>'
            for edge in ("top", "left", "bottom", "right", "insideH", "insideV")
        )
        + "</w:tblBorders>"
    )
    parts = ["<w:tbl><w:tblPr>", borders, "</w:tblPr>"]
    if header:
        parts.append("<w:tr>" + "".join(cell(h, bold=True) for h in header) + "</w:tr>")
    for row in rows:
        parts.append("<w:tr>" + "".join(cell(value) for value in row) + "</w:tr>")
    parts.append("</w:tbl><w:p/>")
    return "".join(parts)


def markdown_to_docx(blocks: Iterable[Block], title: str = "") -> bytes:
    """Convert parsed markdown blocks into the ``word/document.xml`` body."""
    body: list[str] = []
    if title:
        body.append(_paragraph(title, "Heading1"))
    for block in blocks:
        if block.kind == "h1":
            body.append(_paragraph(block.text, "Heading1"))
        elif block.kind == "h2":
            body.append(_paragraph(block.text, "Heading2"))
        elif block.kind == "h3":
            body.append(_paragraph(block.text, "Heading3"))
        elif block.kind == "h4":
            body.append(_paragraph(block.text, "Heading4"))
        elif block.kind == "p":
            body.append(_paragraph(block.text))
        elif block.kind == "quote":
            body.append(_paragraph(block.text, "Quote"))
        elif block.kind == "ul":
            for item in block.items:
                body.append(_list_item(item, ordered=False, index=0))
        elif block.kind == "ol":
            for position, item in enumerate(block.items, start=1):
                body.append(_list_item(item, ordered=True, index=position))
        elif block.kind == "code":
            for line in (block.text or "").split("\n"):
                body.append(_paragraph(line.replace("\t", "    ") or " ", "Code"))
        elif block.kind == "table":
            body.append(_table(block.header, block.rows))
        elif block.kind == "hr":
            body.append('<w:p><w:pPr><w:pBdr><w:bottom w:val="single" w:sz="6" w:space="1" w:color="BFBFBF"/></w:pBdr></w:pPr></w:p>')
    section = (
        '<w:sectPr><w:pgSz w:w="11906" w:h="16838"/>'
        '<w:pgMar w:top="1134" w:right="1134" w:bottom="1134" w:left="1134"/></w:sectPr>'
    )
    xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        f"<w:body>{''.join(body)}{section}</w:body></w:document>"
    )
    return xml.encode("utf-8")


def write_docx(blocks: Iterable[Block], target: Path, title: str = "") -> Path:
    """Write a valid ``.docx`` file from parsed markdown blocks."""
    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    document_xml = markdown_to_docx(blocks, title=title)
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", _CONTENT_TYPES)
        archive.writestr("_rels/.rels", _RELS)
        archive.writestr("word/_rels/document.xml.rels", _DOC_RELS)
        archive.writestr("word/styles.xml", _STYLES)
        archive.writestr("word/document.xml", document_xml)
    return target
