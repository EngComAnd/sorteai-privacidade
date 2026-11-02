#!/usr/bin/env python3
"""Verificação da página da política (spec 004, H-063, H-064, H-069, H-072, H-073 e H-074).

Local (padrão): estrutura, idiomas, ausência de script e de recurso externo, links internos, tamanho e contraste AA.
--publicar: também falha se restar campo pendente (dado real do controlador e versão/vigência preenchidos).
--url BASE: confere o endereço no ar (https, status 200, sem Set-Cookie), ex.: --url https://engcomand.github.io/sorteai-privacidade/privacidade
Saída 0 se tudo passa; 1 caso contrário.
"""
import os, re, sys, urllib.request
from html.parser import HTMLParser

RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
IDIOMAS = {"pt": "pt-BR", "en": "en", "es": "es"}
TAMANHO_MAX = 30 * 1024
EXTERNOS_PERMITIDOS = ("https://policies.google.com/",)

def ler(rel):
    with open(os.path.join(RAIZ, rel), encoding="utf-8") as f:
        return f.read()

class Leitor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags, self.links, self.ids, self.recursos, self.h1, self.pendentes = [], [], set(), [], 0, 0
        self.lang = None; self.alternativas = []; self.nav_links = []; self.em_nav_idioma = False; self.aria_current = 0
    def handle_starttag(self, tag, attrs):
        a = dict(attrs); self.tags.append(tag)
        if tag == "html": self.lang = a.get("lang")
        if tag == "h1": self.h1 += 1
        if "id" in a: self.ids.add(a["id"])
        if tag == "a" and "href" in a: self.links.append(a["href"])
        if tag in ("script", "iframe", "object", "embed", "img", "video", "audio", "form", "input"): self.recursos.append(tag)
        if tag == "link" and a.get("rel") == "alternate": self.alternativas.append(a.get("hreflang"))
        if tag == "link" and a.get("rel") in ("stylesheet", "preload", "preconnect", "icon"): self.recursos.append(f"link rel={a.get('rel')}")
        if "src" in a: self.recursos.append(f"{tag} src")
        if tag == "span" and "pendente" in (a.get("class") or ""): self.pendentes += 1
        if tag == "nav" and a.get("aria-label"): self.em_nav_idioma = True
        if tag == "a" and self.em_nav_idioma and "hreflang" in a:
            self.nav_links.append(a["href"]); self.aria_current += a.get("aria-current") == "page"
    def handle_endtag(self, tag):
        if tag == "nav": self.em_nav_idioma = False

def luminancia(hex_):
    r, g, b = [int(hex_[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)

def razao(a, b):
    la, lb = luminancia(a), luminancia(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)

def contraste(html):
    """Pares de texto e fundo das variáveis CSS, no tema claro e no escuro."""
    css = re.search(r"<style>(.*?)</style>", html, re.S).group(1)
    claro = dict(re.findall(r"--([a-z-]+):(#[0-9A-Fa-f]{6})", css.split("@media (prefers-color-scheme:dark)")[0]))
    escuro = dict(re.findall(r"--([a-z-]+):(#[0-9A-Fa-f]{6})", css.split("@media (prefers-color-scheme:dark)")[1].split("}")[0]))
    erros = []
    for nome, tema in (("claro", claro), ("escuro", escuro)):
        pares = [("texto", "fundo"), ("texto", "superficie"), ("suave", "fundo"), ("suave", "superficie"), ("marca", "fundo"), ("marca", "superficie"), ("pendente-texto", "pendente-fundo")]
        for a, b in pares:
            if razao(tema[a], tema[b]) < 4.5: erros.append(f"contraste {nome}: {a} sobre {b} = {razao(tema[a], tema[b]):.2f} (< 4,5)")
        if razao(tema["fundo"], tema["texto"]) < 4.5: erros.append(f"contraste {nome}: item do idioma atual")
    return erros

def verificar(publicar=False):
    erros = []
    paginas = {i: ler(f"privacidade/{i}/index.html") for i in IDIOMAS}
    ids_por_idioma = {}
    pendentes_por_idioma = {}
    for i, doc in paginas.items():
        l = Leitor(); l.feed(doc); onde = f"privacidade/{i}"
        if l.lang != IDIOMAS[i]: erros.append(f"{onde}: lang={l.lang}, esperado {IDIOMAS[i]}")
        if l.h1 != 1: erros.append(f"{onde}: {l.h1} h1 (esperado 1)")
        if len(doc.encode()) > TAMANHO_MAX: erros.append(f"{onde}: {len(doc.encode())} bytes (> {TAMANHO_MAX})")
        if l.recursos: erros.append(f"{onde}: recurso não permitido {sorted(set(l.recursos))}")
        if len(l.nav_links) != 3 or l.aria_current != 1: erros.append(f"{onde}: o seletor de idioma deve ter 3 links e 1 aria-current")
        if sorted(a for a in l.alternativas if a) != sorted([*IDIOMAS.values(), "x-default"]): erros.append(f"{onde}: hreflang incompleto {l.alternativas}")
        if "<title>" not in doc or 'name="viewport"' not in doc: erros.append(f"{onde}: falta title ou viewport")
        for href in l.links:
            if href.startswith("mailto:"):
                continue
            if href.startswith("http"):
                if not href.startswith(EXTERNOS_PERMITIDOS): erros.append(f"{onde}: link externo não permitido {href}")
            elif href.startswith("#"):
                if href[1:] not in l.ids: erros.append(f"{onde}: âncora {href} sem destino")
            elif not os.path.exists(os.path.normpath(os.path.join(RAIZ, "privacidade", i, href, "index.html"))): erros.append(f"{onde}: link {href} sem página")
        ids_por_idioma[i] = sorted(x for x in l.ids if x not in ("conteudo", "indice"))
        pendentes_por_idioma[i] = l.pendentes
        if publicar and l.pendentes: erros.append(f"{onde}: {l.pendentes} campo(s) pendente(s); preencha com dados reais e a revisão jurídica antes de publicar")
        if re.search(r"\[[A-ZÁÉÍÓÚÇ/@ .,0-9º()-]{3,}\]", re.sub(r'<span class="pendente">.*?</span>', "", doc)): erros.append(f"{onde}: campo entre colchetes fora do destaque")
    if len({tuple(v) for v in ids_por_idioma.values()}) != 1: erros.append(f"seções diferentes entre idiomas: {ids_por_idioma}")
    if len(set(pendentes_por_idioma.values())) != 1: erros.append(f"campos pendentes diferentes entre idiomas: {pendentes_por_idioma}")
    for rel in ("index.html", "404.html", ".nojekyll"):
        if not os.path.exists(os.path.join(RAIZ, rel)): erros.append(f"falta {rel}")
    raiz = ler("index.html"); l = Leitor(); l.feed(raiz)
    if l.recursos: erros.append(f"index.html: recurso não permitido {l.recursos}")
    for i in IDIOMAS:
        if f"privacidade/{i}/" not in raiz: erros.append(f"index.html sem link para {i}")
    site = __import__("json").loads(ler("site.json"))
    for i, doc in paginas.items():
        if f'<link rel="canonical" href="{site["endereco"].rstrip("/")}/privacidade/{i}/">' not in doc: erros.append(f"privacidade/{i}: canonical diferente de site.json")
    quatro = ler("404.html")
    for i in IDIOMAS:
        if f'href="{site["caminho_base"]}privacidade/{i}/"' not in quatro: erros.append(f"404.html: link para {i} fora do caminho base {site['caminho_base']}")
    erros += contraste(paginas["pt"])
    return erros

def verificar_no_ar(base):
    erros = []
    if not base.startswith("https://"): erros.append("o endereço deve ser https")
    for i in IDIOMAS:
        url = f"{base.rstrip('/')}/{i}/"
        try:
            with urllib.request.urlopen(url, timeout=15) as r:
                tipo = r.headers.get("Content-Type", "")
                if r.status != 200: erros.append(f"{url}: status {r.status}")
                if "text/html" not in tipo: erros.append(f"{url}: Content-Type {tipo}")
                if r.headers.get("Set-Cookie"): erros.append(f"{url}: a página define cookie")
        except Exception as e:
            erros.append(f"{url}: {e}")
    return erros

if __name__ == "__main__":
    args = sys.argv[1:]
    erros = verificar("--publicar" in args)
    if "--url" in args: erros += verificar_no_ar(args[args.index("--url") + 1])
    if erros:
        print("\n".join(f"FALHA: {e}" for e in erros)); sys.exit(1)
    print("página verificada")
