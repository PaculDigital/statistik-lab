"""Ekspor REFI-QDA — supaya hasil koding di statistik-lab bisa dibuka &
diuji di NVivo / ATLAS.ti / MAXQDA. (Wulan, 19 Okt 2026)

Standar: REFI-QDA Project 1.0 (urn:QDA-XML:project:1.0) & Codebook 1.0.
Skema XSD resmi diunduh dari arsip qdasoftware.org (Wayback 2021-05-12)
dan dipakai untuk validasi di gerbang uji.

Isi ekspor:
- .qdpx : proyek penuh — Sources (satu TextSource per informan),
  CodeBook (Tema > Kode), Coding (segmen -> kode via posisi karakter),
  Cases (satu Case per informan, membawa jenis internal/eksternal).
- .qdc  : codebook saja (Tema > Kode + deskripsi).

Hanya stdlib (xml.etree, zipfile, uuid) — tanpa dependensi baru.
"""

import io
import uuid
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

NS_P = "urn:QDA-XML:project:1.0"
NS_C = "urn:QDA-XML:codebook:1.0"


def _g():
    return str(uuid.uuid4()).upper()


def _warna(i):
    palet = ["#4E79A7", "#F28E2B", "#E15759", "#76B7B2", "#59A14F",
             "#EDC948", "#B07AA1", "#FF9DA7", "#9C755F", "#BAB0AC"]
    return palet[i % len(palet)]


def _rapikan(nama):
    nama = (nama or "").strip()
    return nama or "Tanpa nama"


def _normal_informan(informan):
    """Samakan bentuk informan → list of dict {nama, teknik, jenis}.

    ⚠️ Wulan 19Okt26: endpoint menerima payload dari BROWSER (localStorage),
    jadi bentuknya tidak dijamin. Dulu `informan` list of STRING atau string
    tunggal atau None langsung bikin 'str' object has no attribute 'get'
    → HTTP 500. Sekarang dinormalkan; yang tak terpakai dibuang.
    """
    if not informan:
        return []
    if isinstance(informan, (str, int, float)):
        informan = [informan]
    if not isinstance(informan, (list, tuple)):
        return []
    hasil = []
    for f in informan:
        if isinstance(f, str):
            nama = f.strip()
            if nama:
                hasil.append({'nama': nama, 'teknik': '', 'jenis': ''})
        elif isinstance(f, dict):
            nama = _rapikan(f.get('nama') or f.get('name') or '')
            if nama:
                hasil.append({'nama': nama,
                              'teknik': _rapikan(f.get('teknik') or ''),
                              'jenis': _rapikan(f.get('jenis') or '')})
    return hasil


def bangun_proyek(nama_proyek, segmen, informan=()):
    """segmen: list dict {teks, kode, tema, informan, teknik, jenis}.
    Hanya segmen yang sudah punya kode & tema yang diekspor.
    Kembalikan bytes .qdpx (zip berisi project.qde).

    Urutan elemen mengikuti XSD resmi: CodeBook, Cases, Sources.
    """
    # ⚠️ Wulan 19Okt26: tahan payload rusak (dari browser, tak dijamin bentuk)
    if not segmen:
        raise ValueError("belum ada segmen yang dikode")
    if not isinstance(segmen, (list, tuple)):
        raise ValueError("segmen harus berupa daftar")
    segmen = [s for s in segmen if isinstance(s, dict)]
    informan = _normal_informan(informan)

    terkode = [s for s in segmen
               if _rapikan(s.get("kode")) and _rapikan(s.get("tema"))]
    if not terkode:
        raise ValueError("belum ada segmen yang dikode")

    ET.register_namespace("", NS_P)
    root = ET.Element("{%s}Project" % NS_P)
    root.set("name", (nama_proyek or "Proyek statistik-lab").strip() or "Proyek statistik-lab")
    root.set("origin", "statistik-lab (bikinaja.id)")
    root.set("creationDateTime", datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))

    # ── data bantu ──
    info_meta = {(_rapikan(f.get("nama"))): f for f in (informan or [])}
    nama_informan = []
    for s in terkode:
        n = _rapikan(s.get("informan"))
        if n not in nama_informan:
            nama_informan.append(n)
    guid_informan = {n: _g() for n in nama_informan}

    # ── CodeBook: Tema (grup) > Kode ──
    guid_kode = {}
    cb = ET.SubElement(root, "CodeBook")
    codes = ET.SubElement(cb, "Codes")
    temas = []
    for s in terkode:
        t = _rapikan(s.get("tema"))
        if t not in temas:
            temas.append(t)
    for i, t in enumerate(temas):
        el_t = ET.SubElement(codes, "Code")
        el_t.set("guid", _g())
        el_t.set("name", t)
        el_t.set("isCodable", "false")
        el_t.set("color", _warna(i))
        d = ET.SubElement(el_t, "Description")
        d.text = "Tema hasil koding di statistik-lab"
        kodes = []
        for s in terkode:
            k = _rapikan(s.get("kode"))
            if _rapikan(s.get("tema")) == t and k not in kodes:
                kodes.append(k)
        for k in kodes:
            g = _g()
            guid_kode[k] = g
            el_k = ET.SubElement(el_t, "Code")
            el_k.set("guid", g)
            el_k.set("name", k)
            el_k.set("isCodable", "true")

    # ── Cases: satu Case per informan (membawa jenis internal/eksternal) ──
    cases = ET.SubElement(root, "Cases")
    for n in nama_informan:
        meta = info_meta.get(n, {})
        c = ET.SubElement(cases, "Case")
        c.set("guid", _g())
        c.set("name", n)
        if meta.get("jenis") or meta.get("teknik"):
            d = ET.SubElement(c, "Description")
            d.text = " · ".join(x for x in
                               [meta.get("jenis"), meta.get("teknik")] if x)
        sr = ET.SubElement(c, "SourceRef")
        sr.set("targetGUID", guid_informan[n])

    # ── Sources: satu TextSource per informan ──
    srcs = ET.SubElement(root, "Sources")
    for n in nama_informan:
        meta = info_meta.get(n, {})
        label = n
        if meta.get("teknik"):
            label += " (%s)" % meta["teknik"]
        if meta.get("jenis"):
            label += " · %s" % meta["jenis"]
        ts = ET.SubElement(srcs, "TextSource")
        ts.set("guid", guid_informan[n])
        ts.set("name", label)
        bagian = []
        pos = 0
        peta_offset = {}
        for idx, s in enumerate(terkode):
            if _rapikan(s.get("informan")) != n:
                continue
            teks = (s.get("teks") or "").strip()
            if bagian:
                bagian.append("\n\n")
                pos += 2
            mulai = pos
            bagian.append(teks)
            pos += len(teks)
            peta_offset[idx] = (mulai, pos)
        pc = ET.SubElement(ts, "PlainTextContent")
        pc.text = "".join(bagian)
        for idx, (mulai, akhir) in peta_offset.items():
            s = terkode[idx]
            sel = ET.SubElement(ts, "PlainTextSelection")
            sel.set("guid", _g())
            sel.set("startPosition", str(mulai))
            sel.set("endPosition", str(akhir))
            cod = ET.SubElement(sel, "Coding")
            cod.set("guid", _g())
            cr = ET.SubElement(cod, "CodeRef")
            cr.set("targetGUID", guid_kode[_rapikan(s.get("kode"))])

    xml = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("project.qde", xml)
    return buf.getvalue()


def bangun_codebook(segmen):
    """Kembalikan bytes .qdc (codebook saja)."""
    terkode = [s for s in segmen
               if (s.get("kode") or "").strip() and (s.get("tema") or "").strip()]
    if not terkode:
        raise ValueError("belum ada segmen yang dikode")
    ET.register_namespace("", NS_C)
    root = ET.Element("{%s}CodeBook" % NS_C)
    root.set("origin", "statistik-lab (bikinaja.id)")
    codes = ET.SubElement(root, "Codes")
    temas = []
    for s in terkode:
        t = _rapikan(s.get("tema"))
        if t not in temas:
            temas.append(t)
    for i, t in enumerate(temas):
        el_t = ET.SubElement(codes, "Code")
        el_t.set("guid", _g())
        el_t.set("name", t)
        el_t.set("isCodable", "false")
        el_t.set("color", _warna(i))
        kodes = []
        for s in terkode:
            k = _rapikan(s.get("kode"))
            if _rapikan(s.get("tema")) == t and k not in kodes:
                kodes.append(k)
        for k in kodes:
            el_k = ET.SubElement(el_t, "Code")
            el_k.set("guid", _g())
            el_k.set("name", k)
            el_k.set("isCodable", "true")
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)
