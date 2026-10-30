"""Entegrasyon akışı görsellerini üretir: docs/assets/akislar/*.svg

Çalıştırma (repo kökünden):  python tools/akis_svg.py
Görseli değiştirmek için SVG'yi elle düzenlemek yerine buradaki adımları güncelleyip yeniden üretin.
"""
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "docs" / "assets" / "akislar"

NAVY = "#253467"
AMBER = "#F9B513"
TEAL = "#0F766E"
INK = "#1F2937"
MUTED = "#6B7280"
LINE = "#D1D5DB"
FONT = "font-family=\"Inter, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif\""
MONO = "font-family=\"'JetBrains Mono', Consolas, 'Courier New', monospace\""

W = 1000
LANE_X = {"sys": 185, "db": 505, "user": 815}
LANE_COLOR = {"sys": NAVY, "db": "#B7860B", "user": TEAL}
LANE_FILL = {"sys": NAVY, "db": AMBER, "user": TEAL}
LANE_TEXT = {"sys": "#FFFFFF", "db": NAVY, "user": "#FFFFFF"}
TOP = 118
ROW = 84


def t(x, y, s, size=14, weight=400, fill=INK, anchor="middle", mono=False, extra=""):
    fam = MONO if mono else FONT
    return (f'<text x="{x}" y="{y}" {fam} font-size="{size}" font-weight="{weight}" '
            f'fill="{fill}" text-anchor="{anchor}" {extra}>{escape(s)}</text>')


def badge(x, y, n, color):
    return (f'<circle cx="{x}" cy="{y}" r="14" fill="{color}"/>'
            + t(x, y + 5, str(n), 14, 700, "#FFFFFF"))


def arrow_defs():
    out = ["<defs>"]
    for key, c in LANE_COLOR.items():
        out.append(f'<marker id="ah-{key}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" '
                   f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{c}"/></marker>')
    out.append("</defs>")
    return "".join(out)


def flow(name, title, lanes, steps, note=None):
    """lanes: {"sys": "Sizin sisteminiz", ...}; steps: (kind, from, to, label, sub)
    kind: "call" (düz ok), "event" (kesikli ok: bildirim/webhook), "act" (şerit içi iş)."""
    h = TOP + ROW * len(steps) + (60 if note else 8)
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" width="{W}" height="{h}" role="img" '
         f'aria-label="{escape(title)}">', arrow_defs(),
         f'<rect x="0.5" y="0.5" width="{W - 1}" height="{h - 1}" rx="14" fill="#FFFFFF" stroke="{LINE}"/>']

    for key, label in lanes.items():
        x = LANE_X[key]
        p.append(f'<line x1="{x}" y1="76" x2="{x}" y2="{h - (50 if note else 14)}" stroke="{LINE}" '
                 f'stroke-width="2" stroke-dasharray="4 6"/>')
        p.append(f'<rect x="{x - 130}" y="20" width="260" height="46" rx="23" fill="{LANE_FILL[key]}"/>')
        p.append(t(x, 49, label, 18, 700, LANE_TEXT[key]))

    for i, (kind, a, b, label, sub) in enumerate(steps):
        n = i + 1
        y = TOP + ROW * i
        color = LANE_COLOR[a]
        if kind == "act":
            x = LANE_X[a]
            bw = 330
            p.append(f'<rect x="{x - bw / 2}" y="{y - 26}" width="{bw}" height="{58 if sub else 46}" rx="10" '
                     f'fill="#F9FAFB" stroke="{color}" stroke-width="1.5"/>')
            p.append(badge(x - bw / 2, y - 26, n, color))
            p.append(t(x, y + 3, label, 17, 600))
            if sub:
                p.append(t(x, y + 23, sub, 13.5, 400, MUTED, mono=True))
            continue
        x1, x2 = LANE_X[a], LANE_X[b]
        d = 1 if x2 > x1 else -1
        dash = ' stroke-dasharray="7 5"' if kind == "event" else ""
        p.append(f'<line x1="{x1 + d * 6}" y1="{y}" x2="{x2 - d * 8}" y2="{y}" stroke="{color}" stroke-width="2.2"'
                 f'{dash} marker-end="url(#ah-{a})"/>')
        left = min(x1, x2)
        p.append(badge(left + 30, y - 18, n, color))
        p.append(t(left + 52, y - 11, label, 17, 600, anchor="start"))
        if sub:
            p.append(t(left + 52, y + 24, sub, 13.5, 400, MUTED, anchor="start", mono=True))

    if note:
        p.append(t(W / 2, h - 22, note, 15, 400, MUTED))
    p.append("</svg>")
    (OUT / f"{name}.svg").write_text("".join(p), encoding="utf-8")


def decision():
    """Hangi akış? karar şeması: dört sonuç kutusu tek sırada."""
    h = 520
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" width="{W}" height="{h}" role="img" '
         f'aria-label="Hangi entegrasyon akışı?">',
         f'<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="9" markerHeight="9" orient="auto">'
         f'<path d="M0,0 L10,5 L0,10 z" fill="{MUTED}"/></marker></defs>',
         f'<rect x="0.5" y="0.5" width="{W - 1}" height="{h - 1}" rx="14" fill="#FFFFFF" stroke="{LINE}"/>']

    def card(x, title, lines, fill, text="#FFFFFF", subfill=None):
        y, w, hh = 300, 232, 150
        p.append(f'<rect x="{x - w / 2}" y="{y}" width="{w}" height="{hh}" rx="14" fill="{fill}"/>')
        p.append(t(x, y + 36, title, 20, 700, text))
        for k, line in enumerate(lines):
            p.append(t(x, y + 70 + k * 22, line, 14.5, 400, subfill or text))

    def q(x, y, w, text):
        p.append(f'<rect x="{x - w / 2}" y="{y}" width="{w}" height="52" rx="26" fill="#F3F4F6" stroke="{LINE}"/>')
        p.append(t(x, y + 32, text, 18, 700))

    def edge(x1, y1, x2, y2):
        p.append(f'<path d="M{x1},{y1} C{x1},{(y1 + y2) / 2} {x2},{(y1 + y2) / 2} {x2},{y2 - 5}" fill="none" '
                 f'stroke="{MUTED}" stroke-width="2" marker-end="url(#ah)"/>')

    def pill(x, y, text):
        w = len(text) * 8 + 26
        p.append(f'<rect x="{x - w / 2}" y="{y - 15}" width="{w}" height="28" rx="14" fill="#FFFFFF" stroke="{LINE}"/>')
        p.append(t(x, y + 4, text, 14, 600, INK))

    cols = [130, 375, 625, 870]
    q(W / 2, 22, 360, "Ne yapmak istiyorsunuz?")
    edge(W / 2, 74, cols[0], 300)
    edge(W / 2, 74, cols[1], 300)
    edge(W / 2, 74, 748, 162)
    q(748, 162, 380, "Nitelikli (yasal) imza gerekli mi?")
    edge(700, 214, cols[2], 300)
    edge(800, 214, cols[3], 300)

    pill(cols[0] + 40, 196, "Kullanıcıya giriş")
    pill(cols[1] + 30, 236, "Belgesiz kimlik teyidi")
    pill(700, 112, "Belge imzalatmak / onaylatmak")
    pill(cols[2] + 20, 262, "Evet")
    pill(cols[3] - 20, 262, "Hayır")

    card(cols[0], "Login", ["Şifresiz, doğrulanmış giriş", "e-imza (Sümen)", "mobil imza"], NAVY, subfill="#DCE3F5")
    card(cols[1], "Kimlik Doğrulama", ["Belgesiz kimlik teyidi", "kimlik kartı NFC + SMS", "+ konum (+ yüz / video)"],
         TEAL, subfill="#D5F0EC")
    card(cols[2], "Belge İmzalama", ["Nitelikli elektronik imza", "ıslak imza yerine geçer", "EIMZA · MOBILE_IMZA"],
         NAVY, subfill="#DCE3F5")
    card(cols[3], "Dijital Onay", ["Kanıtlı, zaman damgalı onay", "e-posta · SMS · kimlik kartı", "*_TIMESTAMP · TCKK_*"],
         AMBER, text=NAVY, subfill=NAVY)
    p.append(t(W / 2, h - 28, "Dijital onay ve kimlik doğrulamada verilen kanıtlar (SMS, konum, kimlik kartı, yüz, video) "
               "JAdES ile mühürlenir.", 15, 400, MUTED))
    p.append("</svg>")
    (OUT / "hangi-akis.svg").write_text("".join(p), encoding="utf-8")


def models():
    """Belge imzalama: merkezi imza ekranı ve uygulama içi imza modellerinin karşılaştırması."""
    h = 440
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" width="{W}" height="{h}" role="img" '
         f'aria-label="Belge imzalama entegrasyon modelleri">',
         f'<defs><marker id="am" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="9" markerHeight="9" orient="auto">'
         f'<path d="M0,0 L10,5 L0,10 z" fill="{MUTED}"/></marker></defs>',
         f'<rect x="0.5" y="0.5" width="{W - 1}" height="{h - 1}" rx="14" fill="#FFFFFF" stroke="{LINE}"/>',
         f'<line x1="{W / 2}" y1="24" x2="{W / 2}" y2="{h - 24}" stroke="{LINE}" stroke-width="2"/>']

    def box(x, y, w, hh, title, sub, fill, text="#FFFFFF", subfill=None):
        p.append(f'<rect x="{x - w / 2}" y="{y}" width="{w}" height="{hh}" rx="12" fill="{fill}"/>')
        p.append(t(x, y + (26 if sub else hh / 2 + 6), title, 16, 700, text))
        if sub:
            p.append(t(x, y + 48, sub, 13, 400, subfill or text))

    def arrow(x1, y1, x2, y2):
        p.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2 - 6}" stroke="{MUTED}" stroke-width="2" marker-end="url(#am)"/>')

    # Sol: merkezi imza ekranı
    cx = 250
    p.append(t(cx, 50, "A · Merkezi imza ekranı", 20, 700, NAVY))
    p.append(t(cx, 74, "Tüm uygulamalar tek imza ekranını kullanır", 14, 400, MUTED))
    apps = [110, 250, 390]
    for i, x in enumerate(apps):
        box(x, 100, 120, 46, f"Uygulama {chr(65 + i)}", None, "#E8ECF7", text=NAVY)
        arrow(x, 146, cx + (i - 1) * 90, 226)
    p.append(t(cx + 150, 196, "imzacı yönlendirilir", 13, 600, MUTED))
    box(cx, 226, 330, 64, "DijitalBelge imza ekranı", "app.dijitalbelge.com/sign/{accessToken}", AMBER, text=NAVY, subfill=NAVY)
    arrow(cx, 290, cx, 336)
    box(cx, 336, 330, 60, "E-imza (Sümen) · mobil imza", "kimlik doğrulama · dijital onay", NAVY, subfill="#DCE3F5")

    # Sağ: uygulama içi imza
    rx = 750
    p.append(t(rx, 50, "B · Uygulama içi imza", 20, 700, TEAL))
    p.append(t(rx, 74, "Her uygulama imzayı kendi ekranında alır", 14, 400, MUTED))
    for i, x in enumerate([635, 865]):
        box(x, 100, 200, 64, f"Uygulama {chr(65 + i)}", "kendi imza ekranı", TEAL, subfill="#D5F0EC")
        arrow(x, 164, x, 226)
        box(x, 226, 200, 60, "Sümen", "signDocument (yerel)", "#E6F4F1", text=TEAL, subfill=TEAL)
        arrow(x, 286, rx + (x - rx) * 0.35, 336)
    box(rx, 336, 330, 60, "DijitalBelge API", "imzalama token'ı · imza doğrulama", AMBER, text=NAVY, subfill=NAVY)
    p.append(t(W / 2, h - 12, "", 1))
    p.append("</svg>")
    (OUT / "imzalama-modelleri.svg").write_text("".join(p), encoding="utf-8")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    decision()
    models()

    three = {"sys": "Sizin sisteminiz", "db": "DijitalBelge", "user": "İmzacı"}

    flow("belge-imzalama", "Merkezi imza ekranıyla belge imzalama akışı",
         {"sys": "Sizin uygulamanız", "db": "DijitalBelge", "user": "İmzacı (imza ekranı)"}, [
        ("call", "sys", "db", "Süreç oluştur", "POST /process-instances"),
        ("call", "sys", "db", "Belge ekle (PDF / taslak)", "POST …/document/single"),
        ("call", "sys", "db", "İmzacı ekle (imza türüyle)", "EIMZA · MOBILE_IMZA"),
        ("call", "sys", "db", "Süreci başlat", "PUT …/status/start"),
        ("event", "db", "user", "İmza ekranına yönlendirme", "/sign/{accessToken} · e-posta / SMS"),
        ("act", "user", None, "İmza ekranında imzalar", "e-imza (Sümen) · mobil imza"),
        ("event", "db", "sys", "Webhook", "DOCUMENT_SIGNED (allSigned)"),
        ("call", "sys", "db", "İmzalı belgeyi indir", "GET …/document/{id}/file"),
    ], note="Birden çok imzacıda 5–7. adımlar her imzacı için sırayla tekrarlanır.")

    flow("belge-imzalama-uygulama-ici", "Uygulama içi belge imzalama akışı",
         {"sys": "Sizin uygulamanız", "db": "DijitalBelge", "user": "Sümen (imzacının PC'si)"}, [
        ("call", "sys", "db", "Süreç, belge ve imzacıyı hazırla", "process-instances · document · signers"),
        ("call", "sys", "db", "Süreci başlat, accessToken al", "PUT …/status/start"),
        ("call", "sys", "db", "Belgenin imzalama token'ını al", "GET /files/process/{accessToken}"),
        ("act", "sys", None, "İmzacı kendi ekranınızda PIN girer", "cihaz / sertifika seçimi"),
        ("call", "sys", "user", "signDocument komutu", "token · pin · slot · order"),
        ("call", "user", "db", "Özeti al, kartla imzala, gönder", "…/hash → …/sign/{uid}"),
        ("event", "user", "sys", "İmza sonucu", "WebSocket yanıtı"),
        ("event", "db", "sys", "Webhook", "DOCUMENT_SIGNED"),
    ], note="İmzacı uygulamanızdan hiç ayrılmaz; DijitalBelge imza ekranı kullanılmaz.")

    flow("dijital-onay", "Dijital onay akışı", {"sys": "Sizin sisteminiz", "db": "DijitalBelge", "user": "Onaylayan"}, [
        ("call", "sys", "db", "Süreç oluştur", "POST /process-instances"),
        ("call", "sys", "db", "Belge ekle", "POST …/document/single"),
        ("call", "sys", "db", "Onaylayan ekle (onay türüyle)", "EMAIL / SMSOTP_TIMESTAMP · TCKK_*"),
        ("call", "sys", "db", "Süreci başlat", "PUT …/status/start"),
        ("event", "db", "user", "Onay daveti", "e-posta / SMS bağlantısı"),
        ("act", "user", None, "Kimliğini kanıtlar, onaylar", "e-posta · SMS · kimlik kartı"),
        ("act", "db", None, "Kanıtlar mühürlenir", "zaman damgalı JAdES"),
        ("event", "db", "sys", "Webhook", "DOCUMENT_SIGNED"),
        ("call", "sys", "db", "Belge ve kanıtı indir", "GET …/document/{id}/files"),
    ], note="Onay türü yalnızca 3. adımda değişir; akışın geri kalanı tüm türlerde aynıdır.")

    flow("kimlik-dogrulama", "Kimlik doğrulama akışı", {"sys": "Sizin sisteminiz", "db": "DijitalBelge", "user": "Üye"}, [
        ("call", "sys", "db", "Süreç oluştur", "DIJITAL_KIMLIK_DOGRULAMA"),
        ("act", "sys", None, "processId ↔ üye eşlemesi", "kendi veritabanınızda"),
        ("call", "sys", "db", "Üyeyi sürece bağla", "POST …/signers/all-documents"),
        ("call", "sys", "db", "Süreci başlat", "PUT …/status/start"),
        ("event", "db", "user", "Doğrulama bağlantısı", "SMS / e-posta / QR"),
        ("act", "user", None, "Kimlik kartını okutur (NFC)", "+ SMS + konum (+ yüz/video)"),
        ("event", "db", "sys", "Webhook", "DOCUMENT_SIGNED"),
        ("act", "sys", None, "Üyeyi doğrulandı işaretler", "isteğe bağlı: kanıtı indir"),
    ], note="Belge imzalanmaz; yalnızca kişinin kimliğini kanıtlayan mühürlü bir kanıt dosyası üretilir.")

    flow("login-eimza", "E-imza ile login akışı",
         {"sys": "Sizin sisteminiz", "db": "DijitalBelge", "user": "Kullanıcı (Sümen)"}, [
        ("call", "sys", "db", "Login işlemi başlat", "POST /auth/tx"),
        ("event", "sys", "user", "Token'ı Sümen'e iletir", "yerel WebSocket"),
        ("act", "user", None, "E-imza kartıyla imzalar", "PIN"),
        ("call", "user", "db", "İmzayı gönderir", "Sümen → DijitalBelge"),
        ("act", "db", None, "Sertifika ve imza doğrulanır", "audit log oluşur"),
        ("call", "sys", "db", "Sonucu sorgula", "GET /auth/tx/{txId}"),
        ("call", "sys", "db", "Audit log'u oku, giriş yaptır", "GET /auth/tx/{txId}/audit"),
    ])

    flow("login-mobil", "Mobil imza ile login akışı",
         {"sys": "Sizin sisteminiz", "db": "DijitalBelge", "user": "Kullanıcı (telefon)"}, [
        ("call", "sys", "db", "Operatör listesini al", "GET /auth/operators"),
        ("call", "sys", "db", "Login işlemi başlat", "POST /auth/{op}/mobiltx"),
        ("event", "db", "user", "Operatörden imza isteği", "Turkcell · Vodafone · Türk Telekom"),
        ("act", "user", None, "Telefonda PIN ile onaylar", "SIM kart imzası"),
        ("call", "sys", "db", "Durumu sorgula (polling)", "GET /auth/{op}/mobil/{txId}"),
        ("call", "sys", "db", "Audit log'u oku, giriş yaptır", "GET /auth/tx/{txId}/audit"),
    ])
    print("SVG'ler üretildi:", ", ".join(sorted(f.name for f in OUT.glob("*.svg"))))


if __name__ == "__main__":
    main()
