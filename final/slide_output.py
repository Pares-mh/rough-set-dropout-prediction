"""Write editable PowerPoint slides and a matching PDF from one layout."""
from dataclasses import dataclass, field
from copy import deepcopy
from pathlib import Path
from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZipFile

from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas


W, H = 960, 540
FONT = "Arial"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
P = "http://schemas.openxmlformats.org/presentationml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG = "http://schemas.openxmlformats.org/package/2006/relationships"
CT = "http://schemas.openxmlformats.org/package/2006/content-types"
WINDOWS_FONTS = Path("C:/Windows/Fonts")
for face, filename in (("Body", "arial.ttf"), ("Bold", "arialbd.ttf")):
    if (WINDOWS_FONTS / filename).exists():
        pdfmetrics.registerFont(TTFont(face, str(WINDOWS_FONTS / filename)))


def pdf_font(bold):
    face = "Bold" if bold else "Body"
    if face in pdfmetrics.getRegisteredFontNames():
        return face
    return "Helvetica-Bold" if bold else "Helvetica"


@dataclass
class Slide:
    background: str
    notes: str
    objects: list = field(default_factory=list)

    def text(self, text, x, y, width, size, color, bold=False):
        lines = text.splitlines()
        height = len(lines) * size * 1.18 + 2
        measured = max(pdfmetrics.stringWidth(line, pdf_font(bold), size) for line in lines)
        if measured > width - 2:
            raise ValueError(f"Slide line too wide ({measured:.0f} > {width}): {text}")
        self._add("text", x, y, width, height, (lines, size, color, bold))

    def box(self, x, y, width, height, color):
        self._add("box", x, y, width, height, color)

    def image(self, path, x, y, width, height):
        self._add("image", x, y, width, height, Path(path))

    def _add(self, kind, x, y, width, height, value):
        if x < 0 or y < 0 or x + width > W + .01 or y + height > H + .01:
            raise ValueError(f"{kind} outside the slide: {(x, y, width, height)}")
        self.objects.append((kind, x, y, width, height, value))


def write_pdf(slides, path):
    canvas = Canvas(str(path), pagesize=(W, H))
    canvas.setTitle("Rough-set decision rules for early student dropout prediction")
    canvas.setAuthor("Md Pares Mahmud, Abu Hanif, and Shirsha Mitra")
    for slide in slides:
        canvas.setFillColor(HexColor(slide.background))
        canvas.rect(0, 0, W, H, stroke=0, fill=1)
        for kind, x, y, w, h, value in slide.objects:
            if kind == "box":
                canvas.setFillColor(HexColor(value))
                canvas.rect(x, H - y - h, w, h, stroke=0, fill=1)
            elif kind == "image":
                canvas.drawImage(str(value), x, H - y - h, width=w, height=h, mask="auto")
            else:
                lines, size, color, bold = value
                canvas.setFillColor(HexColor(color))
                canvas.setFont(pdf_font(bold), size)
                for i, line in enumerate(lines):
                    canvas.drawString(x, H - y - size * (0.95 + i * 1.18), line)
        canvas.showPage()
    canvas.save()


def _rels(entries):
    return f'<Relationships xmlns="{PKG}">' + "".join(
        f'<Relationship Id="{i}" Type="{R}/{kind}" Target="{target}"/>'
        for i, kind, target in entries) + "</Relationships>"


def _emu(value):
    return round(value * 12700)


def _fill(color):
    return f'<a:solidFill><a:srgbClr val="{color.lstrip("#")}"/></a:solidFill>'


def _shape_xml(obj, index, image_rel=None):
    kind, x, y, w, h, value = obj
    transform = (f'<a:xfrm><a:off x="{_emu(x)}" y="{_emu(y)}"/>'
                 f'<a:ext cx="{_emu(w)}" cy="{_emu(h)}"/></a:xfrm>')
    rect = '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
    identity = f'<p:cNvPr id="{index}" name="{kind} {index}"/>'
    if kind == "image":
        return (f'<p:pic><p:nvPicPr>{identity}<p:cNvPicPr/><p:nvPr/></p:nvPicPr>'
                f'<p:blipFill><a:blip r:embed="{image_rel}"/><a:stretch><a:fillRect/>'
                f'</a:stretch></p:blipFill><p:spPr>{transform}{rect}</p:spPr></p:pic>')
    txbox = ' txBox="1"' if kind == "text" else ""
    nv = f'<p:nvSpPr>{identity}<p:cNvSpPr{txbox}/><p:nvPr/></p:nvSpPr>'
    style = _fill(value) if kind == "box" else "<a:noFill/>"
    geometry = f"<p:spPr>{transform}{rect}{style}<a:ln><a:noFill/></a:ln></p:spPr>"
    if kind == "box":
        return f"<p:sp>{nv}{geometry}</p:sp>"
    lines, size, color, bold = value
    run = (f'<a:rPr lang="en-US" sz="{round(size * 100)}" b="{int(bold)}">'
           f'{_fill(color)}<a:latin typeface="{FONT}"/></a:rPr>')
    paragraphs = "".join(
        f'<a:p><a:pPr><a:lnSpc><a:spcPts val="{round(size * 118)}"/></a:lnSpc></a:pPr>'
        f'<a:r>{run}<a:t>{escape(line)}</a:t></a:r></a:p>' for line in lines)
    body = ('<p:txBody><a:bodyPr wrap="none" lIns="0" tIns="0" rIns="0" bIns="0"/>'
            f'<a:lstStyle/>{paragraphs}</p:txBody>')
    return f"<p:sp>{nv}{geometry}{body}</p:sp>"


def _slide_xml(slide, shapes):
    return (
        f'<p:sld xmlns:p="{P}" xmlns:a="{A}" xmlns:r="{R}" showMasterSp="0">'
        f'<p:cSld><p:bg><p:bgPr>{_fill(slide.background)}<a:effectLst/></p:bgPr></p:bg>'
        '<p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/>'
        '</p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/>'
        '<a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
        f'{shapes}</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>'
    )


def write_pptx(slides, path, scaffold):
    for prefix, uri in (("p", P), ("a", A), ("r", R)):
        ET.register_namespace(prefix, uri)
    with ZipFile(scaffold) as source:
        parts = {n: source.read(n) for n in source.namelist()
                 if not n.startswith(("ppt/slides/", "ppt/notesSlides/", "ppt/media/"))
                 and n != "docProps/thumbnail.jpeg"}
        notes_template = source.read("ppt/notesSlides/notesSlide1.xml")
    for name, data in parts.items():
        if name.endswith(".xml") and name.startswith(
            ("ppt/slideMasters/", "ppt/slideLayouts/", "ppt/notesMasters/")
        ):
            # The base theme contains an undeclared legacy DrawingML attribute.
            parts[name] = data.replace(b' smtClean="0"', b'').replace(b' smtClean="1"', b'')
    presentation = ET.fromstring(parts["ppt/presentation.xml"])
    slide_ids = presentation.find(f"{{{P}}}sldIdLst")
    slide_ids.clear()
    size = presentation.find(f"{{{P}}}sldSz")
    size.attrib = {"cx": str(_emu(W)), "cy": str(_emu(H)), "type": "screen16x9"}
    pres_rels = ET.fromstring(parts["ppt/_rels/presentation.xml.rels"])
    notes_master_rel = next(rel.get("Id") for rel in pres_rels
                            if rel.attrib["Type"] == f"{R}/notesMaster")
    if presentation.find(f"{{{P}}}notesMasterIdLst") is None:
        notes_master_list = ET.Element(f"{{{P}}}notesMasterIdLst")
        ET.SubElement(notes_master_list, f"{{{P}}}notesMasterId", {f"{{{R}}}id": notes_master_rel})
        presentation.insert(1, notes_master_list)
    for rel in list(pres_rels):
        if rel.attrib["Type"] == f"{R}/slide":
            pres_rels.remove(rel)
    types = ET.fromstring(parts["[Content_Types].xml"])
    for item in list(types):
        if item.get("PartName", "").startswith(("/ppt/slides/", "/ppt/notesSlides/")):
            types.remove(item)

    for i, slide in enumerate(slides, 1):
        rel = f"rId{100 + i}"
        ET.SubElement(slide_ids, f"{{{P}}}sldId", {"id": str(255 + i), f"{{{R}}}id": rel})
        ET.SubElement(pres_rels, f"{{{PKG}}}Relationship",
                      {"Id": rel, "Type": f"{R}/slide", "Target": f"slides/slide{i}.xml"})
        slide_rels = [("rId1", "slideLayout", "../slideLayouts/slideLayout7.xml"),
                      ("rId2", "notesSlide", f"../notesSlides/notesSlide{i}.xml")]
        shapes = []
        for index, obj in enumerate(slide.objects, 2):
            img_rel = None
            if obj[0] == "image":
                img_rel = f"rId{len(slide_rels) + 1}"
                name = f"final-{i}-{index}.png"
                slide_rels.append((img_rel, "image", f"../media/{name}"))
                parts[f"ppt/media/{name}"] = obj[-1].read_bytes()
            shapes.append(_shape_xml(obj, index, img_rel))
        parts[f"ppt/slides/slide{i}.xml"] = _slide_xml(slide, "".join(shapes))
        parts[f"ppt/slides/_rels/slide{i}.xml.rels"] = _rels(slide_rels)
        notes = ET.fromstring(notes_template)
        note_body = next(
            sp.find(f"{{{P}}}txBody") for sp in notes.iter(f"{{{P}}}sp")
            if any(ph.get("type") == "body" for ph in sp.iter(f"{{{P}}}ph"))
        )
        old_paragraphs = note_body.findall(f"{{{A}}}p")
        template = old_paragraphs[0]
        for paragraph in old_paragraphs:
            note_body.remove(paragraph)
        for line in slide.notes.split("\n"):
            paragraph = deepcopy(template)
            paragraph.find(f".//{{{A}}}t").text = line
            note_body.append(paragraph)
        parts[f"ppt/notesSlides/notesSlide{i}.xml"] = ET.tostring(notes, encoding="utf-8")
        parts[f"ppt/notesSlides/_rels/notesSlide{i}.xml.rels"] = _rels([
            ("rId1", "notesMaster", "../notesMasters/notesMaster1.xml"),
            ("rId2", "slide", f"../slides/slide{i}.xml"),
        ])
        for kind, stem in (("slides", "slide"), ("notesSlides", "notesSlide")):
            ET.SubElement(types, f"{{{CT}}}Override",
                          {"PartName": f"/ppt/{kind}/{stem}{i}.xml",
                           "ContentType": f"application/vnd.openxmlformats-officedocument.presentationml.{stem}+xml"})
    parts["ppt/presentation.xml"] = ET.tostring(presentation, encoding="utf-8")
    ET.register_namespace("", PKG)
    parts["ppt/_rels/presentation.xml.rels"] = ET.tostring(pres_rels, encoding="utf-8")
    package_rels = ET.fromstring(parts["_rels/.rels"])
    for rel in list(package_rels):
        if rel.get("Target") == "docProps/thumbnail.jpeg":
            package_rels.remove(rel)
    parts["_rels/.rels"] = ET.tostring(package_rels, encoding="utf-8")
    ET.register_namespace("", CT)
    parts["[Content_Types].xml"] = ET.tostring(types, encoding="utf-8")
    # Build fresh metadata. Inherited date attributes use lexical QName values,
    # which lose their prefix binding when reserialized by ElementTree.
    parts["docProps/core.xml"] = (
        '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"'
        ' xmlns:dc="http://purl.org/dc/elements/1.1/">'
        '<dc:title>Rough-set decision rules for early student dropout prediction</dc:title>'
        '<dc:subject>Information Granular Computing final project</dc:subject>'
        '<dc:creator>Md Pares Mahmud, Abu Hanif, and Shirsha Mitra</dc:creator>'
        '</cp:coreProperties>'
    )
    parts["docProps/app.xml"] = (
        '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties">'
        f'<PresentationFormat>Widescreen</PresentationFormat><Slides>{len(slides)}</Slides>'
        f'<Notes>{len(slides)}</Notes></Properties>'
    )
    with ZipFile(path, "w", ZIP_DEFLATED) as result:
        for name, data in parts.items():
            result.writestr(name, data)
