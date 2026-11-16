"""Build the static Ramdam Games site from content/games.json into docs/."""
import datetime
import hashlib
import html
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
MONTHS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
          "septembre", "octobre", "novembre", "décembre"]
FONTS = ("https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700;12..96,800"
         "&family=Figtree:wght@400;500;600;700&family=Zilla+Slab:wght@500;700&family=VT323&display=swap")

e = html.escape


def asset_version(name):
    with open(os.path.join(DOCS, "assets", name), "rb") as f:
        return hashlib.sha1(f.read()).hexdigest()[:8]


def fr_date(iso):
    d = datetime.date.fromisoformat(iso)
    day = "1er" if d.day == 1 else str(d.day)
    return f"{day} {MONTHS[d.month - 1]} {d.year}"


def mark_svg(size=34):
    return (f'<svg class="mark" width="{size}" height="{size}" viewBox="0 0 64 64" aria-hidden="true">'
            '<path d="M32 2l6.4 9.2 10.8-3.1.6 11.2 10.5 4-6.4 9.2 6.4 9.2-10.5 4-.6 11.2-10.8-3.1L32 62l-6.4-9.2'
            '-10.8 3.1-.6-11.2-10.5-4 6.4-9.2-6.4-9.2 10.5-4 .6-11.2 10.8 3.1z" fill="var(--brand)"/>'
            '<path d="M23 44V20h10.5c5.6 0 9 3 9 7.6 0 3.3-1.8 5.6-4.8 6.6L43.5 44h-6.4l-5.1-9.2h-3.2V44z'
            'm5.8-14h4.2c2.4 0 3.7-1 3.7-2.6 0-1.7-1.3-2.6-3.7-2.6h-4.2z" fill="var(--brand-ink)"/></svg>')


def page(*, title, description, body, theme, depth, path, og_image=None, body_class=""):
    up = "../" * depth
    base = "https://ramdam-games.github.io/"
    og = ""
    if og_image:
        image = f"{base}assets/{og_image}?v={asset_version(og_image)}"
        og = "\n".join([
            f'<meta property="og:image" content="{image}">',
            '<meta property="og:image:width" content="1200">',
            '<meta property="og:image:height" content="630">',
            f'<meta property="og:image:alt" content="{e(title)}">',
            f'<meta name="twitter:image" content="{image}">',
        ])
    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Ramdam Games">
<meta property="og:locale" content="fr_FR">
<meta name="theme-color" content="{THEME_COLORS[theme]}">
<meta property="og:url" content="{base}{path}">
{og}
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{up}assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="{up}assets/site.css?v={asset_version("site.css")}">
</head>
<body class="t-{theme} {body_class}">
{nav(up)}
{body}
{footer(up)}
<script src="{up}assets/site.js?v={asset_version("site.js")}" defer></script>
</body>
</html>
"""


THEME_COLORS = {"studio": "#ff5a36", "fourriere": "#e0603a", "bloomstead": "#7ccf4d"}


def nav(up):
    return f"""<header class="nav">
  <div class="nav-in">
    <a class="brand" href="{up}index.html">{mark_svg()}<span>Ramdam Games</span></a>
    <nav aria-label="Navigation principale">
      <a href="{up}index.html#jeux">Jeux</a>
      <a href="{up}journal.html">Journal</a>
      <a href="{up}index.html#studio">Studio</a>
    </nav>
  </div>
</header>"""


def footer(up):
    s = DATA["studio"]
    games = "".join(f'<a href="{up}jeux/{g["slug"]}/index.html">{e(g["title"])}</a>' for g in DATA["games"])
    return f"""<footer class="foot">
  <div class="foot-in">
    <div class="foot-brand">{mark_svg(42)}<div><strong>Ramdam Games</strong><span>{e(s["tagline"])}</span></div></div>
    <div class="foot-cols">
      <div><h4>Jeux</h4>{games}</div>
      <div><h4>Suivre</h4><a href="{up}journal.html">Journal de développement</a><a href="{e(s["discord"])}">Discord</a><a href="{e(s["github"])}">GitHub</a></div>
    </div>
  </div>
  <p class="foot-note">© 2026 Ramdam Games</p>
</footer>"""


def pills(g):
    items = [e(p) for p in g["platforms"]] + [e(g["players"])]
    return "".join(f"<li>{i}</li>" for i in items)


def status(g):
    return f'<span class="status status-{g["status_kind"]}">{e(g["status"])}</span>'


def game_title(g, cls="title"):
    if g["theme"] == "bloomstead":
        return f'<h1 class="{cls} title-img"><img src="{{up}}assets/img/bloomstead/logo.png" alt="Bloomstead" width="1600" height="480"></h1>'
    return f'<h1 class="{cls} title-sign"><span>La</span> Fourrière</h1>'


def entry_html(g, c, up, show_game=False):
    head = ""
    if show_game:
        head = f'<a class="entry-game" href="{up}jeux/{g["slug"]}/index.html">{e(g["title"])}</a>'
    sid = f'{g["slug"]}-{c["version"].replace(" ", "-").lower()}'
    lang = f' lang="{c["lang"]}"' if c.get("lang") else ""
    parts = [f'<article class="entry t-{g["theme"]}" id="{e(sid)}" data-game="{g["slug"]}">',
             f'<header>{head}<h3>{e(c["version"])}</h3><time datetime="{c["date"]}">{fr_date(c["date"])}</time></header>']
    for key, label in (("new", "Nouveautés"), ("improved", "Améliorations"), ("fixed", "Corrections")):
        if c.get(key):
            cls = ' class="fix"' if key == "fixed" else ""
            parts.append(f'<h4>{label}</h4><ul{cls}{lang}>' + "".join(f"<li>{e(x)}</li>" for x in c[key]) + "</ul>")
    if c.get("tech"):
        n = c["tech"]
        parts.append(f'<p class="tech">Et {n} changement{"s" if n > 1 else ""} technique{"s" if n > 1 else ""} qui ne se voi{"en" if n > 1 else ""}t pas en jeu.</p>')
    parts.append("</article>")
    return "".join(parts)


def all_entries():
    out = []
    for g in DATA["games"]:
        for c in g["changelog"]:
            out.append((c["date"], g, c))
    out.sort(key=lambda t: t[0], reverse=True)
    return out


def build_home():
    up = ""
    panes = []
    for i, g in enumerate(DATA["games"]):
        title = game_title(g, "pane-title").replace("{up}", up).replace("<h1", "<h2").replace("</h1>", "</h2>")
        panes.append(f"""<article class="pane t-{g['theme']}" style="background-image:url('assets/img/{g['card_image']}')">
      <a class="pane-link" href="jeux/{g['slug']}/index.html" aria-label="{e(g['title'])}"></a>
      <div class="pane-shade"></div>
      <div class="pane-body">
        <p class="pane-genre">{e(g['genre'])}</p>
        {title}
        <p class="pane-short">{e(g['short'])}</p>
        <div class="pane-meta">{status(g)}<ul class="pills">{pills(g)}</ul></div>
        <div class="pane-actions"><a class="btn" href="jeux/{g['slug']}/index.html">Découvrir le jeu</a><a class="btn ghost" href="jeux/{g['slug']}/journal.html">Journal</a></div>
      </div>
    </article>""")
    news = "".join(news_card(g, c, up) for _, g, c in all_entries()[:4])
    s = DATA["studio"]
    about = "".join(f"<p>{e(p)}</p>" for p in s["about"])
    n_versions = sum(len(g["changelog"]) for g in DATA["games"])
    cast = "assets/img/fourriere/cast/"
    perches = "".join(
        f'<img class="perch {cls}" src="{src}" alt="" style="--d:{d}">'
        for cls, src, d in (
            ("p-girafe back", cast + "girafe.webp", ".55"),
            ("p-autruche back", cast + "autruche.webp", ".45"),
            ("p-bernard", cast + "bernard.webp", "1"),
            ("p-lama", cast + "lama.webp", ".8"),
            ("p-sprout", "assets/img/bloomstead/mascot.png", ".7"),
            ("p-poule", cast + "poule.webp", ".9"),
            ("p-monique", cast + "monique.webp", "1.25"),
            ("p-manchot", cast + "manchot.webp", "1.1"),
        ))
    runners = [("lapin", .5), ("zebre", 1.1), ("elephant", 1.45), ("cochon", .75), ("poule", .55),
               ("chasseur-filet", 1.6, "chaser"), ("autruche", 1.5), ("lion", 1), ("mouton", .8),
               ("chasseur-fusil", 1.3, "hunter"), ("chasseur-prise", 1.55, "chaser"),
               ("camionnette", 1.1, "van")]
    parade = "".join(
        f'<img class="{r[2] if len(r) > 2 else "runner"}" src="{cast}{r[0]}.webp" alt="" style="--h:{r[1]}">'
        for r in runners) * 2
    village_items = (
        ("village/eglise", 3, 96, 1, ".25"),
        ("village/granderoue", 49, 100, 1, ".25"),
        ("village/chateaueau", 84, 82, 1, ".25"),
        ("village/commerce1", -1, 74, 2, ".4"),
        ("village/lampadaire", 15, 50, 3, ".5"),
        ("village/mairie", 21, 64, 2, ".4"),
        ("village/lilas", 42, 56, 2, ".45"),
        ("village/manege", 57, 40, 3, ".55"),
        ("village/pavillon3", 70, 56, 2, ".4"),
        ("village/cypres", 95, 66, 2, ".45"),
        ("cast/maire", 33, 34, 4, ".7"),
        ("village/mascotte", 11, 30, 4, ".7"),
        ("cast/garde", 52, 33, 4, ".7"),
        ("cast/mmepichon", 83, 30, 4, ".7"),
    )
    village = "".join(
        f'<img src="assets/img/fourriere/{src}.webp" alt="" style="left:{left}%;height:{h}%;z-index:{z};--d:{d};--i:{i}">'
        for i, (src, left, h, z, d) in enumerate(village_items))
    games_links = " et ".join(f'<a href="jeux/{g["slug"]}/index.html">{e(g["title"])}</a>' for g in DATA["games"])
    body = f"""<main>
<section class="ramdam" aria-label="Ramdam Games">
  <div class="ramdam-in">
    <h1 class="wordmark" aria-label="Ramdam Games">
      <span class="word" aria-hidden="true"><span>R</span><span>a</span><span>m</span><span>d</span><span>a</span><span>m</span></span>
      {perches}
      <span class="games" aria-hidden="true">games</span>
    </h1>
    <p class="ramdam-sub">Studio de jeux indépendant, en France. Tout le zoo s'est échappé ici : {games_links}.</p>
    <a class="ramdam-down" href="#jeux">Voir les jeux</a>
    <div class="village" aria-hidden="true">{village}</div>
  </div>
  <div class="parade" aria-hidden="true"><div class="parade-track">{parade}</div></div>
</section>

<section class="home-hero" id="jeux">
  <div class="home-head wrap">
    <h2>Les jeux</h2>
    <p class="lead">Choisis un jeu pour voir ses images, ce qu'on y fait et tout ce qui a changé depuis la dernière version.</p>
  </div>
  <div class="picker">
    {''.join(panes)}
  </div>
</section>

<section class="wrap block">
  <div class="block-head"><h2>Dernières nouvelles</h2><a class="more" href="journal.html">Tout le journal</a></div>
  <div class="news">{news}</div>
</section>

<section class="wrap block studio" id="studio">
  <div class="studio-text">
    <h2>Le studio</h2>
    {about}
    <p class="studio-links"><a class="btn" href="{e(s['discord'])}">Rejoindre le Discord</a><a class="btn ghost" href="{e(s['github'])}">GitHub</a></p>
  </div>
  <dl class="studio-facts">
    <div><dt>{len(DATA['games'])}</dt><dd>jeux en cours</dd></div>
    <div><dt>{n_versions}</dt><dd>versions dans le journal</dd></div>
    <div><dt>2026</dt><dd>année de création</dd></div>
  </dl>
</section>
</main>"""
    write("index.html", page(title="Ramdam Games", description=DATA["studio"]["share"],
                             body=body, theme="studio", depth=0, path="", og_image="og/home.jpg", body_class="home"))


def news_card(g, c, up):
    first = (c.get("new") or c.get("improved") or c.get("fixed"))[0]
    count = len(c.get("new", [])) + len(c.get("improved", [])) + len(c.get("fixed", []))
    sid = f'{g["slug"]}-{c["version"].replace(" ", "-").lower()}'
    return f"""<a class="news-card t-{g['theme']}" href="{up}jeux/{g['slug']}/journal.html#{e(sid)}">
      <span class="news-game">{e(g['title'])}</span>
      <strong>{e(c['version'])}</strong>
      <time datetime="{c['date']}">{fr_date(c['date'])}</time>
      <p>{e(first)}</p>
      <span class="news-count">{count} changement{'s' if count > 1 else ''}</span>
    </a>"""


def build_game(g):
    up = "../../"
    slug = g["slug"]
    img = f"{up}assets/img/"
    title = game_title(g).replace("{up}", up)
    pitch = "".join(f"<p>{e(p)}</p>" for p in g["pitch"])
    facts = "".join(f"<div><dt>{e(k)}</dt><dd>{e(v)}</dd></div>" for k, v in g["facts"])
    features = "".join(f"""<div class="feature">
      <figure><img src="{img}{f['image']}" alt="" loading="lazy" width="1600" height="900"></figure>
      <div><h3>{e(f['title'])}</h3><p>{e(f['text'])}</p></div>
    </div>""" for f in g["features"])

    extra = ""
    if g.get("trailer"):
        extra += f"""<section class="wrap block" id="bande-annonce">
  <div class="block-head"><h2>Bande-annonce</h2></div>
  <div class="trailer"><video controls preload="none" playsinline poster="{img}{g['trailer_poster']}"><source src="{e(g['trailer'])}" type="video/mp4"></video></div>
  <p class="credit">{e(g['trailer_credit'])}</p>
</section>"""
    if g.get("cast"):
        tiles = "".join(f"""<figure class="tile"><img src="{img}fourriere/cast/{k}.webp" alt="{e(n)}" loading="lazy"><figcaption><strong>{e(n)}</strong><span>{e(d)}</span></figcaption></figure>""" for k, n, d in g["cast"])
        people = "".join(f"""<figure class="person"><img src="{img}fourriere/cast/{k}.webp" alt="{e(n)}" loading="lazy"><figcaption><strong>{e(n)}</strong><span>{e(d)}</span></figcaption></figure>""" for k, n, d in g["people"])
        gear = "".join(f"""<figure class="gear-item"><img src="{img}fourriere/cast/{k}.webp" alt="" loading="lazy"><figcaption>{e(n)}</figcaption></figure>""" for k, n in g["gear"])
        extra += f"""<section class="cast-band">
  <div class="wrap block">
    <div class="block-head"><h2>{e(g['cast_title'])}</h2><p>{e(g['cast_lead'])}</p></div>
    <div class="cast">{tiles}</div>
  </div>
</section>
<section class="wrap block">
  <div class="block-head"><h2>{e(g['people_title'])}</h2></div>
  <div class="people">{people}</div>
  <div class="gear">{gear}</div>
</section>"""
    if g.get("machines"):
        tiles = "".join(f"""<figure class="machine"><img src="{img}bloomstead/machines/{k}.png" alt="" loading="lazy" width="100" height="96"><figcaption><strong>{e(n)}</strong><span>{e(d)}</span></figcaption></figure>""" for k, n, d in g["machines"])
        extra += f"""<section class="wrap block">
  <div class="block-head"><h2>{e(g['machines_title'])}</h2><p>Elles rejoignent la boîte à outils un niveau après l'autre, chacune avec sa portée et son astuce.</p></div>
  <div class="machines">{tiles}</div>
</section>"""

    folder = g["theme"]
    n = len(g["gallery"])
    bigs = next((b for b in range(0, n // 2 + 1) if (n + 3 * b) % 4 == 0), 0)
    big_at = {round(i * n / bigs) for i in range(bigs)} if bigs else set()
    gallery = "".join(f"""<a class="shot{' big' if i in big_at else ''}" href="{img}{folder}/{k}.jpg" data-caption="{e(c)}"><img src="{img}{folder}/thumbs/{k}.jpg" alt="{e(c)}" loading="lazy" width="640" height="360"></a>""" for i, (k, c) in enumerate(g["gallery"]))
    where = "".join(f"""<div class="door"><h3>{e(p)}</h3><span class="status status-soon">{e(s)}</span><p>{e(t)}</p></div>""" for p, s, t in g["where"])
    links = "".join(f'<a href="{e(u)}">{e(n)}</a>' for n, u in g.get("links", []))
    recent = "".join(entry_html(g, c, up) for c in g["changelog"][:2])
    trailer_btn = '<a class="btn" href="#bande-annonce">Voir la bande-annonce</a>' if g.get("trailer") else '<a class="btn" href="#images">Voir les images</a>'
    if g.get("hero_card"):
        hc = g["hero_card"]
        pops = "".join(f'<img class="pop pop-{i}" src="{img}fourriere/cast/{k}.webp" alt="">' for i, k in enumerate(hc["pops"]))
        hero_open = '<section class="game-hero hero-card">'
        hero_art = f'<figure class="hero-photo"><img class="photo" src="{img}{g["hero_image"]}" alt="{e(hc["alt"])}" width="1600" height="900">{pops}</figure>'
    else:
        hero_open = f"""<section class="game-hero" style="background-image:url('{img}{g['hero_image']}')">"""
        hero_art = ""
    body = f"""<main>
{hero_open}
  <div class="game-hero-in wrap">
    {hero_art}
    <p class="crumbs"><a href="{up}index.html">Ramdam Games</a> <span aria-hidden="true">/</span> {e(g['title'])}</p>
    {title}
    <p class="genre">{e(g['genre'])}</p>
    <p class="lead">{e(g['short'])}</p>
    <div class="hero-actions">{trailer_btn}<a class="btn ghost" href="journal.html">Journal de développement</a></div>
    <div class="pane-meta">{status(g)}<ul class="pills">{pills(g)}</ul></div>
  </div>
</section>

<section class="wrap block intro">
  <div class="intro-text">{pitch}</div>
  <dl class="facts">{facts}</dl>
</section>

<section class="wrap block features">{features}</section>
{extra}
<section class="wrap block" id="images">
  <div class="block-head"><h2>Images</h2><p>Captures du jeu tel qu'il est aujourd'hui.</p></div>
  <div class="gallery">{gallery}</div>
</section>

<section class="wrap block">
  <div class="block-head"><h2>Où jouer</h2></div>
  <div class="doors">{where}</div>
  {f'<p class="small-links">{links}</p>' if links else ''}
</section>

<section class="wrap block">
  <div class="block-head"><h2>Dernières versions</h2><a class="more" href="journal.html">Tout le journal</a></div>
  <div class="entries">{recent}</div>
</section>
</main>
<dialog class="lightbox" aria-label="Image agrandie">
  <button class="lb-close" type="button" aria-label="Fermer">×</button>
  <button class="lb-prev" type="button" aria-label="Image précédente">‹</button>
  <figure><img alt=""><figcaption></figcaption></figure>
  <button class="lb-next" type="button" aria-label="Image suivante">›</button>
</dialog>"""
    write(f"jeux/{slug}/index.html", page(title=f"{g['title']} | Ramdam Games", description=g["short"], body=body,
                                         theme=g["theme"], depth=2, path=f"jeux/{slug}/", og_image=f"og/{slug}.jpg"))

    toc = "".join(f'<a href="#{g["slug"]}-{c["version"].replace(" ", "-").lower()}"><strong>{e(c["version"])}</strong><span>{fr_date(c["date"])}</span></a>' for c in g["changelog"])
    entries = "".join(entry_html(g, c, up) for c in g["changelog"])
    jbody = f"""<main class="wrap journal-page">
  <header class="journal-head">
    <p class="crumbs"><a href="{up}index.html">Ramdam Games</a> <span aria-hidden="true">/</span> <a href="index.html">{e(g['title'])}</a> <span aria-hidden="true">/</span> Journal</p>
    <h1>Journal de développement</h1>
    <p class="lead">Tout ce qui change dans {e(g['title'])}, version après version.</p>
  </header>
  <div class="journal">
    <nav class="toc" aria-label="Versions">{toc}</nav>
    <div class="entries">{entries}</div>
  </div>
</main>"""
    write(f"jeux/{slug}/journal.html", page(title=f"Journal de {g['title']} | Ramdam Games",
                                           description=f"Notes de version et journal de développement de {g['title']}.",
                                           body=jbody, theme=g["theme"], depth=2, path=f"jeux/{slug}/journal.html", og_image=f"og/{slug}.jpg"))


def build_journal():
    up = ""
    chips = '<button type="button" class="chip on" data-filter="all">Tous les jeux</button>' + "".join(
        f'<button type="button" class="chip t-{g["theme"]}" data-filter="{g["slug"]}">{e(g["title"])}</button>' for g in DATA["games"])
    entries = "".join(entry_html(g, c, up, show_game=True) for _, g, c in all_entries())
    body = f"""<main class="wrap journal-page">
  <header class="journal-head">
    <p class="kicker">Ramdam Games</p>
    <h1>Journal de développement</h1>
    <p class="lead">Les notes de version de tous les jeux, de la plus récente à la plus ancienne.</p>
    <div class="chips" role="group" aria-label="Filtrer par jeu">{chips}</div>
  </header>
  <div class="entries all">{entries}</div>
</main>"""
    write("journal.html", page(title="Journal | Ramdam Games", description="Notes de version de La Fourrière et de Bloomstead.",
                               body=body, theme="studio", depth=0, path="journal.html", og_image="og/home.jpg"))


def build_404():
    body = """<main class="wrap block lost"><h1>Page introuvable</h1><p>Elle a dû s'échapper avec le reste du zoo.</p><p><a class="btn" href="/index.html">Retour à l'accueil</a></p></main>"""
    write("404.html", page(title="Page introuvable | Ramdam Games", description="Page introuvable.", body=body,
                           theme="studio", depth=0, path="404.html"))


def build_redirects():
    """The Bloomstead site moved from /bloomstead-privacy/ to /bloomstead/: keep the old links alive."""
    for name in ("index.html", "privacy.html", "versions.html", "game.html"):
        target = "/bloomstead/" + ("" if name == "index.html" else name)
        write(f"bloomstead-privacy/{name}", f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Bloomstead</title>
<meta name="robots" content="noindex">
<link rel="canonical" href="https://ramdam-games.github.io{target}">
<meta http-equiv="refresh" content="0; url={target}">
<script>location.replace("{target}" + location.hash);</script>
</head>
<body><p>This page moved to <a href="{target}">ramdam-games.github.io{target}</a>.</p></body>
</html>
""")


def write(rel, text):
    path = os.path.join(DOCS, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def main():
    global DATA
    with open(os.path.join(ROOT, "content", "games.json"), encoding="utf-8") as f:
        DATA = json.load(f)
    for g in DATA["games"]:
        with open(os.path.join(ROOT, "content", "journal", g["slug"] + ".json"), encoding="utf-8") as f:
            g["changelog"] = json.load(f)
    build_home()
    for g in DATA["games"]:
        build_game(g)
    build_journal()
    build_404()
    build_redirects()
    with open(os.path.join(DOCS, "assets", "favicon.svg"), "w", encoding="utf-8") as f:
        f.write(mark_svg(64).replace('class="mark" ', 'xmlns="http://www.w3.org/2000/svg" ')
                .replace("var(--brand-ink)", "#1b0f0b").replace("var(--brand)", "#ff5a36"))
    open(os.path.join(DOCS, ".nojekyll"), "w").close()
    print("built")


DATA = {}

if __name__ == "__main__":
    main()
