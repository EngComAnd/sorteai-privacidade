# Página da política de privacidade do SorteAí

Site estático (HTML e CSS embutido, **sem script, sem cookie, sem recurso externo**) com a política em **português, inglês e espanhol** e um seletor de idioma por links. Implementa a spec 004 (`specs/fase-1/004-pagina-politica-privacidade/`).

> **Onde vive o texto publicado (spec 004, D-02):** o repositório público [EngComAnd/sorteai-privacidade](https://github.com/EngComAnd/sorteai-privacidade), criado em 2026-11-02 com o **Pages desligado**. Esta pasta é a cópia de partida; depois do merge do PR #25, mude o texto **só lá** (por pull request) e remova esta pasta do repositório do app, para não haver duas fontes.

```text
index.html                    # escolha do idioma
privacidade/{pt,en,es}/       # a política (endereço final: <domínio>/privacidade/<idioma>/)
404.html  .nojekyll
fonte/{pt,en,es}.html         # o texto de cada idioma (edite aqui)
versao.json                   # versão e vigência exibidas
scripts/gerar-pagina.py       # fonte -> páginas
scripts/verificar-pagina.py   # verificação (local, --publicar, --url)
```

## Editar e verificar

Rode os comandos a partir da raiz deste site (a pasta `site-privacidade/` do repositório do app, ou a raiz do repositório `sorteai-privacidade`).

```bash
python3 scripts/gerar-pagina.py      # regenera as páginas
python3 scripts/verificar-pagina.py  # estrutura, idiomas, sem script, links, tamanho e contraste AA
```

As três versões têm de ter as mesmas seções e os mesmos campos pendentes; a verificação confere. Não edite `privacidade/*/index.html` à mão: são gerados.

## Antes de publicar (H-068, H-069)

Decisões já aplicadas (2026-11-02, do responsável pelo produto): base legal dos anúncios = a do AdMob (consentimento onde a lei exige; nas demais regiões o Google é controlador independente); garantias de transferência internacional = as descritas na política do Google, com link; foro = o do domicílio do consumidor; público-alvo = 13 anos ou mais; **versão 1**, vigência da publicação até a atualização, conforme as leis de cada país.

Controlador e contato (2026-11-02): sem pessoa jurídica por ora, a política usa o **responsável como pessoa física**: nome, cidade/UF e o e-mail da conta dele. O CPF e o endereço completo ficam **fora** da página (a LGPD pede identificar o controlador, não expor o documento). Quando existir a pessoa jurídica, troque o controlador, o encarregado e o e-mail em `fonte/*.html`.

1. Revise o texto em `fonte/*.html` (nos três idiomas). O texto em inglês e em espanhol é tradução feita pelo agente a partir do português e **precisa de revisão**, como o restante (revisão jurídica recomendada).
2. Ajuste `versao.json` se mudar a versão e rode o gerador.
3. `python3 scripts/verificar-pagina.py --publicar` deve passar (hoje passa; falha se algum campo voltar a ficar pendente).
4. Mudou o que o app faz com dados (novo SDK, nova permissão, novo dado)? Revise a política **no mesmo lançamento** e a Data safety da Play (H-071).

## Publicar (decisões e ações do dono)

Já feito (2026-11-02, autorizado): repositório público `EngComAnd/sorteai-privacidade` com este conteúdo, branch `main` protegida (pull request obrigatório) e **Pages desligado**. O fluxo `Publicar página` só roda **manualmente**.

**Fase 1: domínio do GitHub Pages, sem domínio próprio** (spec 004, emenda 2, decisão de 2026-11-02). O endereço é `https://engcomand.github.io/sorteai-privacidade/privacidade/{pt,en,es}/`; `site.json` guarda o endereço e o caminho base (`/sorteai-privacidade/`). Domínio próprio fica para a Fase 2: aí o caminho base vira `/` e entra o arquivo `CNAME`.

Falta, quando você decidir:
1. Revisão jurídica do texto.
2. Settings → Pages → Source: **GitHub Actions**; depois Actions → "Publicar página" → Run workflow (ele roda `verificar-pagina.py --publicar`).
3. `python3 scripts/verificar-pagina.py --publicar --url https://engcomand.github.io/sorteai-privacidade/privacidade` (status 200, https, HTML, sem cookie).
4. Cadastrar a variável `POLITICA_PRIVACIDADE_URL` = `https://engcomand.github.io/sorteai-privacidade/privacidade/` (com a barra final) em Settings → Secrets and variables → Actions → Variables do repositório do app, e o mesmo endereço (`.../privacidade/pt/`) na Play Console e no AdMob.
5. Ao migrar para domínio próprio (Fase 2): versões já instaladas do app seguem apontando para o endereço do GitHub; confira o redirecionamento antes (spec 004, emenda 2, item 3).
