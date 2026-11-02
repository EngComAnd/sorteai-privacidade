#!/usr/bin/env python3
"""Gera as páginas estáticas da política de privacidade do SorteAí a partir de fonte/<idioma>.html.

Saída: privacidade/<idioma>/index.html (pt, en, es), index.html (raiz, escolha do idioma) e 404.html.
O endereço e o caminho base vêm de site.json (Fase 1: domínio do GitHub Pages; com domínio próprio, o caminho base vira "/").
Sem script, sem fonte externa, sem imagem: CSS embutido, cores do design system (claro e escuro).
Versão e vigência (texto por idioma) vêm de versao.json; vazias, a página mostra os campos pendentes em destaque (não publicar).
Uso: python3 scripts/gerar-pagina.py
"""
import html, json, os

RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

IDIOMAS = ["pt", "en", "es"]
TEXTOS = {
    "pt": dict(lang="pt-BR", nome="Português", titulo="Política de Privacidade", app="SorteAí",
               resumo="Como o SorteAí trata os seus dados: sem cadastro, sem servidor, sorteios só no seu aparelho e anúncios não personalizados.",
               pular="Ir para o conteúdo", idioma="Idioma", versao="Versão", vigencia="Vigência",
               indice="Nesta página", pendente_aviso="Campos em destaque ainda precisam ser preenchidos antes da publicação.",
               rodape="Este texto descreve o que o aplicativo faz hoje. Se o app mudar o que faz com dados, esta página muda no mesmo lançamento.",
               secoes=["Quem somos", "O que o SorteAí faz com os seus dados", "Anúncios (Google AdMob)", "Bases legais", "Compartilhamento e transferência internacional", "Crianças e adolescentes", "Seus direitos", "Segurança", "Alterações e contato"]),
    "en": dict(lang="en", nome="English", titulo="Privacy Policy", app="SorteAí",
               resumo="How SorteAí handles your data: no sign-up, no server, draws stay on your device and ads are non-personalized.",
               pular="Skip to content", idioma="Language", versao="Version", vigencia="Effective",
               indice="On this page", pendente_aviso="Highlighted fields must still be filled in before publication.",
               rodape="This text describes what the app does today. If the app changes what it does with data, this page changes in the same release.",
               secoes=["Who we are", "What SorteAí does with your data", "Ads (Google AdMob)", "Legal bases", "Sharing and international transfer", "Children and teenagers", "Your rights", "Security", "Changes and contact"]),
    "es": dict(lang="es", nome="Español", titulo="Política de Privacidad", app="SorteAí",
               resumo="Cómo SorteAí trata tus datos: sin registro, sin servidor, los sorteos quedan en tu dispositivo y los anuncios no son personalizados.",
               pular="Ir al contenido", idioma="Idioma", versao="Versión", vigencia="Vigencia",
               indice="En esta página", pendente_aviso="Los campos resaltados aún deben completarse antes de la publicación.",
               rodape="Este texto describe lo que la app hace hoy. Si la app cambia lo que hace con los datos, esta página cambia en el mismo lanzamiento.",
               secoes=["Quiénes somos", "Qué hace SorteAí con tus datos", "Anuncios (Google AdMob)", "Bases legales", "Comparticipación y transferencia internacional", "Niños y adolescentes", "Tus derechos", "Seguridad", "Cambios y contacto"]),
}
IDS = ["quem", "dados", "anuncios", "bases", "compartilhamento", "criancas", "direitos", "seguranca", "alteracoes"]

# Cores do design system (docs/referencia/design-system/tokens.json): background, surface, ink, ink-muted, line, marca.
CSS = """
:root{--fundo:#F3F5F9;--superficie:#FFFFFF;--texto:#0E1B2C;--suave:#5A6676;--linha:#D9DEE7;--marca:#2440B8;--pendente-fundo:#FFE9A8;--pendente-texto:#3D2A00}
@media (prefers-color-scheme:dark){:root{--fundo:#0E1116;--superficie:#161C25;--texto:#EAF2F7;--suave:#8E9DB0;--linha:#2A3340;--marca:#9DB2FF;--pendente-fundo:#5C4400;--pendente-texto:#FFEFC2}}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--fundo);color:var(--texto);font:1.0625rem/1.65 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
.pular{position:absolute;left:-999px;top:0;background:var(--texto);color:var(--fundo);padding:.75rem 1rem;z-index:10}
.pular:focus{left:1rem;top:1rem}
header,main,footer{max-width:46rem;margin:0 auto;padding:0 1rem}
header{padding-top:1.5rem}
.marca{font-weight:700;font-size:1.25rem;letter-spacing:.01em}
h1{font-size:1.75rem;line-height:1.25;margin:.5rem 0 .75rem}
h2{font-size:1.25rem;line-height:1.3;margin:2rem 0 .5rem}
a{color:var(--marca);text-underline-offset:.15em}
a:focus-visible,summary:focus-visible{outline:3px solid var(--marca);outline-offset:2px;border-radius:4px}
.idiomas{display:flex;flex-wrap:wrap;gap:.5rem;align-items:center;margin:1rem 0;padding:0;list-style:none}
.idiomas li{display:contents}
.idiomas .rotulo{color:var(--suave);font-size:.9rem;margin-inline-end:.25rem}
.idiomas a{display:inline-flex;align-items:center;min-height:2.75rem;padding:0 1rem;border:1px solid var(--linha);border-radius:999px;background:var(--superficie);color:var(--texto);text-decoration:none}
.idiomas a[aria-current="page"]{background:var(--texto);color:var(--fundo);border-color:var(--texto);font-weight:600}
.meta{color:var(--suave);font-size:.95rem;margin:0 0 1rem}
.resumo{margin:0 0 1rem}
nav.indice{background:var(--superficie);border:1px solid var(--linha);border-radius:12px;padding:.75rem 1rem;margin:1rem 0}
nav.indice p{margin:.25rem 0;font-weight:600}
nav.indice ol{margin:.25rem 0;padding-inline-start:1.25rem}
.aviso{border:1px dashed var(--suave);border-radius:8px;padding:.5rem .75rem;font-size:.95rem}
ul,ol{padding-inline-start:1.25rem}
li{margin:.35rem 0}
table{border-collapse:collapse;width:100%;margin:.5rem 0;background:var(--superficie)}
th,td{border:1px solid var(--linha);padding:.6rem .75rem;text-align:start;vertical-align:top}
th{background:var(--fundo)}
.pendente{background:var(--pendente-fundo);color:var(--pendente-texto);border-bottom:2px dashed currentColor;padding:0 .2em;border-radius:3px}
footer{padding-bottom:3rem;color:var(--suave);font-size:.95rem;border-top:1px solid var(--linha);margin-top:2.5rem;padding-top:1rem}
.lista-idiomas{list-style:none;padding:0}
.lista-idiomas a{display:block;padding:1rem;border:1px solid var(--linha);border-radius:12px;background:var(--superficie);color:var(--texto);text-decoration:none;font-weight:600;margin:.5rem 0}
@media print{.idiomas,.pular,nav.indice{display:none}body{background:#fff;color:#000}}
"""

def ler(rel):
    with open(os.path.join(RAIZ, rel), encoding="utf-8") as f:
        return f.read()

def gravar(rel, conteudo):
    caminho = os.path.join(RAIZ, rel)
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8", newline="\n") as f:
        f.write(conteudo)

def campo(valor, modelo):
    return html.escape(valor) if valor else f'<span class="pendente">[{modelo}]</span>'

def seletor(atual, prefixo):
    t = TEXTOS[atual]
    itens = []
    for i in IDIOMAS:
        marca = ' aria-current="page"' if i == atual else ""
        itens.append(f'<li><a href="{prefixo}{i}/" hreflang="{TEXTOS[i]["lang"]}" lang="{TEXTOS[i]["lang"]}"{marca}>{TEXTOS[i]["nome"]}</a></li>')
    return f'<nav aria-label="{html.escape(t["idioma"])}"><ul class="idiomas"><li class="rotulo">{html.escape(t["idioma"])}:</li>{"".join(itens)}</ul></nav>'

def cabecalho_html(titulo, descricao, lang, alternativas, canonico=""):
    return (f'<!doctype html>\n<html lang="{lang}">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            '<meta name="color-scheme" content="light dark">\n'
            f'<title>{html.escape(titulo)}</title>\n<meta name="description" content="{html.escape(descricao)}">\n'
            f'{canonico}{alternativas}<style>{CSS}</style>\n</head>\n')

def pagina_politica(idioma, versao, site=None):
    site = site or json.loads(ler("site.json"))
    t = TEXTOS[idioma]
    vigencia = versao["vigencia"].get(idioma, "") if isinstance(versao["vigencia"], dict) else versao["vigencia"]
    corpo = ler(f"fonte/{idioma}.html")
    titulo = f'{t["titulo"]} — {t["app"]}'
    alternativas = "".join(f'<link rel="alternate" hreflang="{TEXTOS[i]["lang"]}" href="../{i}/">\n' for i in IDIOMAS)
    alternativas += '<link rel="alternate" hreflang="x-default" href="../en/">\n'
    indice = "".join(f'<li><a href="#{ident}">{html.escape(nome)}</a></li>' for ident, nome in zip(IDS, t["secoes"]))
    canonico = f'<link rel="canonical" href="{site["endereco"].rstrip("/")}/privacidade/{idioma}/">\n'
    return (cabecalho_html(titulo, t["resumo"], t["lang"], alternativas, canonico) +
            f'<body>\n<a class="pular" href="#conteudo">{html.escape(t["pular"])}</a>\n'
            f'<header>\n<div class="marca">{t["app"]}</div>\n{seletor(idioma, "../")}\n</header>\n'
            f'<main id="conteudo">\n<h1>{html.escape(t["titulo"])}</h1>\n'
            f'<p class="meta">{html.escape(t["versao"])}: {campo(versao["versao"], "AAAA.MM.DD-N")} · {html.escape(t["vigencia"])}: {campo(vigencia, "DATA")}</p>\n'
            f'<p class="resumo">{html.escape(t["resumo"])}</p>\n'
            f'<nav class="indice" aria-labelledby="indice"><p id="indice">{html.escape(t["indice"])}</p><ol>{indice}</ol></nav>\n'
            f'{corpo}</main>\n<footer><p>{html.escape(t["rodape"])}</p></footer>\n</body>\n</html>\n')

def pagina_raiz():
    alternativas = "".join(f'<link rel="alternate" hreflang="{TEXTOS[i]["lang"]}" href="privacidade/{i}/">\n' for i in IDIOMAS)
    itens = "".join(f'<li><a href="privacidade/{i}/" hreflang="{TEXTOS[i]["lang"]}" lang="{TEXTOS[i]["lang"]}">{TEXTOS[i]["nome"]} — {html.escape(TEXTOS[i]["titulo"])}</a></li>' for i in IDIOMAS)
    return (cabecalho_html("SorteAí — Privacidade / Privacy / Privacidad", "SorteAí: política de privacidade em português, inglês e espanhol.", "pt-BR", alternativas) +
            '<body>\n<header><div class="marca">SorteAí</div></header>\n<main>\n<h1>Privacidade · Privacy · Privacidad</h1>\n'
            f'<ul class="lista-idiomas">{itens}</ul>\n</main>\n</body>\n</html>\n')

def pagina_404(site=None):
    site = site or json.loads(ler("site.json"))
    base = site["caminho_base"]
    itens = "".join(f'<li><a href="{base}privacidade/{i}/" lang="{TEXTOS[i]["lang"]}">{TEXTOS[i]["nome"]}</a></li>' for i in IDIOMAS)
    return (cabecalho_html("404 — SorteAí", "Página não encontrada.", "pt-BR", "") +
            '<body>\n<header><div class="marca">SorteAí</div></header>\n<main>\n<h1>404</h1>\n'
            '<p>Página não encontrada · Page not found · Página no encontrada</p>\n'
            f'<ul class="lista-idiomas">{itens}</ul>\n</main>\n</body>\n</html>\n')

def main():
    versao = json.loads(ler("versao.json"))
    for i in IDIOMAS:
        gravar(f"privacidade/{i}/index.html", pagina_politica(i, versao))
    gravar("index.html", pagina_raiz())
    gravar("404.html", pagina_404())
    gravar(".nojekyll", "")
    print("páginas geradas:", ", ".join(f"privacidade/{i}/" for i in IDIOMAS))

if __name__ == "__main__":
    main()
