"""Deterministic SVG, HTML, and Markdown artifact templates."""

from __future__ import annotations

import html
from typing import Any


def _trace(tokens: dict[str, Any], refs: tuple[str, ...]) -> str:
    company = tokens["company"]
    lines = [
        "STUDIO TRACE",
        "Label: FICTIONAL CONCEPT",
        f"Fictional company: {company['name']}",
        f"Tagline: {company['tagline']}",
        f"Token version: {tokens['schema_version']}",
        f"Decision refs: {', '.join(refs)}",
    ]
    return "<!--\n" + "\n".join(lines) + "\n-->\n"


def _html_shell(tokens: dict[str, Any], title: str, content: str, refs: tuple[str, ...], extra_css: str = "") -> str:
    company = tokens["company"]
    colors = tokens["palette"]
    type_scale = tokens["typography"]
    esc = html.escape
    css = f"""<style>
:root {{
  --color-primary: {colors['primary']}; --color-ink: {colors['ink']};
  --color-paper: {colors['paper']}; --color-accent: {colors['accent']};
  --color-muted: {colors['muted']};
}}
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: var(--color-paper); color: var(--color-ink); font-family: "{type_scale['body']['family']}"; font-size: {type_scale['body']['size_px']}px; line-height: 1.55; }}
h1, h2, h3 {{ font-family: "{type_scale['heading']['family']}"; line-height: 1.12; }}
a {{ color: var(--color-primary); }}
.site-header, .site-footer {{ display: flex; align-items: center; justify-content: space-between; gap: 24px; padding: 22px clamp(20px, 6vw, 88px); }}
.brand {{ color: var(--color-ink); font-weight: 700; text-decoration: none; }}
.fictional {{ color: var(--color-primary); font-size: 12px; letter-spacing: .12em; text-transform: uppercase; }}
.wrap {{ width: min(1120px, calc(100% - 40px)); margin: 0 auto; }}
.hero {{ padding: clamp(56px, 12vw, 144px) 0; }}
.hero h1 {{ max-width: 850px; margin: 0 0 22px; font-family: "{type_scale['display']['family']}"; font-size: clamp(42px, 8vw, {type_scale['display']['size_px']}px); }}
.lede {{ max-width: 670px; font-size: 20px; }}
.button {{ display: inline-block; padding: 12px 18px; border-radius: 4px; background: var(--color-primary); color: var(--color-paper); text-decoration: none; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 18px; padding: 40px 0 80px; }}
.card {{ border: 1px solid var(--color-muted); border-radius: 8px; padding: 22px; background: var(--color-paper); }}
.surface {{ background: var(--color-muted); padding: 28px; border-radius: 8px; }}
.small {{ font-size: 13px; }}
{extra_css}
@media (max-width: 640px) {{ .site-header {{ align-items: flex-start; flex-direction: column; }} .hero {{ padding: 56px 0; }} }}
</style>"""
    return (
        _trace(tokens, refs)
        + "<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
        + f"<title>{esc(title)}</title>{css}</head><body>"
        + f"<header class=\"site-header\"><a class=\"brand\" href=\"#top\">{esc(company['name'])}</a><span class=\"fictional\">Fictional concept</span></header>"
        + content
        + f"<footer class=\"site-footer small\"><span>{esc(company['name'])}</span><span>{esc(company['tagline'])}</span><span>Fictional concept</span></footer>"
        + "</body></html>\n"
    )


def _svg(tokens: dict[str, Any], title: str, body: str, refs: tuple[str, ...], view_box: str = "0 0 800 480") -> str:
    return (
        _trace(tokens, refs)
        + f"<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"{view_box}\" role=\"img\" aria-label=\"{html.escape(title, quote=True)}\">"
        + f"<title>{html.escape(title)}</title>{body}</svg>\n"
    )


def _markdown(tokens: dict[str, Any], body: str, refs: tuple[str, ...]) -> str:
    return _trace(tokens, refs) + body.rstrip() + "\n"


def _logo_shapes(tokens: dict[str, Any]) -> str:
    colors = tokens["palette"]
    mark = tokens["logo"]["concept"]
    rotation = tokens["logo"]["rotation_degrees"]
    count = tokens["logo"]["unit_count"]
    if mark == "orbit":
        shapes = f"<circle cx=\"100\" cy=\"100\" r=\"54\" fill=\"none\" stroke=\"{colors['primary']}\" stroke-width=\"18\"/><circle cx=\"154\" cy=\"82\" r=\"13\" fill=\"{colors['accent']}\"/>"
    elif mark == "beacon":
        shapes = f"<path d=\"M100 38 L151 153 L49 153 Z\" fill=\"{colors['primary']}\"/><circle cx=\"100\" cy=\"104\" r=\"15\" fill=\"{colors['paper']}\"/>"
    elif mark == "woven grid":
        shapes = "".join(f"<rect x=\"{61 + (i % 2) * 48}\" y=\"{61 + (i // 2) * 48}\" width=\"38\" height=\"38\" rx=\"9\" fill=\"{colors['primary'] if i % 2 == 0 else colors['accent']}\"/>" for i in range(4))
    else:
        shapes = f"<path d=\"M55 145 V55 H145 V145\" fill=\"none\" stroke=\"{colors['primary']}\" stroke-width=\"18\" stroke-linecap=\"round\" stroke-linejoin=\"round\"/><circle cx=\"100\" cy=\"100\" r=\"{count * 4}\" fill=\"{colors['accent']}\"/>"
    return f"<g transform=\"rotate({rotation} 100 100)\">{shapes}</g>"


def _base_svg_text(tokens: dict[str, Any], footer_y: int = 445) -> str:
    c = tokens["company"]
    palette = tokens["palette"]
    font = tokens["typography"]["body"]["family"]
    return (
        f"<rect width=\"800\" height=\"480\" fill=\"{palette['paper']}\"/>"
        f"<text x=\"40\" y=\"{footer_y}\" fill=\"{palette['ink']}\" font-family=\"{font}\" font-size=\"14\">{html.escape(c['name'])} | {html.escape(c['tagline'])}</text>"
        f"<text x=\"40\" y=\"468\" fill=\"{palette['primary']}\" font-family=\"{font}\" font-size=\"10\" letter-spacing=\"2\">FICTIONAL CONCEPT</text>"
    )


def _color_sheet(tokens: dict[str, Any]) -> str:
    labels = ("primary", "ink", "paper", "accent", "muted")
    colors = tokens["palette"]
    swatches = "".join(
        f"<g transform=\"translate({40 + i * 144} 90)\"><rect width=\"120\" height=\"170\" rx=\"8\" fill=\"{colors[key]}\"/><text x=\"0\" y=\"198\" fill=\"{colors['ink']}\" font-family=\"{tokens['typography']['body']['family']}\" font-size=\"14\">{key}</text><text x=\"0\" y=\"220\" fill=\"{colors['ink']}\" font-family=\"{tokens['typography']['mono']['family']}\" font-size=\"12\">{colors[key]}</text></g>"
        for i, key in enumerate(labels)
    )
    return _svg(tokens, "Color system", _base_svg_text(tokens) + swatches + f"<text x=\"40\" y=\"54\" fill=\"{colors['ink']}\" font-family=\"{tokens['typography']['heading']['family']}\" font-size=\"28\">Color system</text>", ("visual_identity",), "800 480")


def _type_specimen(tokens: dict[str, Any]) -> str:
    c = tokens["company"]
    colors = tokens["palette"]
    pieces = [f"<rect width=\"800\" height=\"480\" fill=\"{colors['paper']}\"/>"]
    y = 105
    for role, label in (("display", "Display"), ("heading", "Heading"), ("body", "Body"), ("mono", "Mono")):
        style = tokens["typography"][role]
        pieces.append(f"<text x=\"42\" y=\"{y}\" fill=\"{colors['primary']}\" font-family=\"{style['family']}\" font-size=\"{min(style['size_px'], 48)}\" font-weight=\"{style['weight']}\">{label}: {html.escape(c['tagline'])}</text>")
        y += 78
    pieces.append(_base_svg_text(tokens))
    return _svg(tokens, "Typography specimen", "".join(pieces), ("visual_identity",), "800 480")


def _logo(tokens: dict[str, Any]) -> str:
    colors = tokens["palette"]
    c = tokens["company"]
    font = tokens["typography"]["heading"]["family"]
    body = (
        f"<rect width=\"800\" height=\"480\" fill=\"{colors['paper']}\"/>"
        f"<g transform=\"translate(300 70) scale(1.5)\">{_logo_shapes(tokens)}</g>"
        f"<text x=\"400\" y=\"345\" text-anchor=\"middle\" fill=\"{colors['ink']}\" font-family=\"{font}\" font-size=\"34\">{html.escape(c['name'])}</text>"
        f"<text x=\"400\" y=\"382\" text-anchor=\"middle\" fill=\"{colors['ink']}\" font-family=\"{tokens['typography']['body']['family']}\" font-size=\"17\">{html.escape(c['tagline'])}</text>"
        f"<text x=\"400\" y=\"435\" text-anchor=\"middle\" fill=\"{colors['primary']}\" font-family=\"{tokens['typography']['mono']['family']}\" font-size=\"11\" letter-spacing=\"2\">FICTIONAL CONCEPT</text>"
    )
    return _svg(tokens, "Fictional company mark", body, ("company_name", "visual_identity"))


def _landing(tokens: dict[str, Any]) -> str:
    c = tokens["company"]
    esc = html.escape
    cards = "".join(f"<article class=\"card\"><span class=\"fictional\">{esc(p['id'])}</span><h2>{esc(p['title'])}</h2><p>{esc(p['message'])}</p></article>" for p in tokens["messaging_pillars"])
    content = (
        f"<main id=\"top\" class=\"wrap\"><section class=\"hero\"><span class=\"fictional\">Fictional concept</span><h1>{esc(c['tagline'])}</h1>"
        f"<p class=\"lede\">{esc(c['positioning'])}</p><a class=\"button\" href=\"#approach\">Explore the idea</a></section>"
        f"<section id=\"approach\"><h2>From listening to a next step</h2><div class=\"grid\">{cards}</div></section>"
        f"<section class=\"surface\"><p class=\"fictional\">A fictional product concept</p><h2>{esc(c['product_name'])}</h2><p>Gather feedback, keep its context, and make a thoughtful decision visible to the team.</p></section></main>"
    )
    return _html_shell(tokens, c["name"] + " | Fictional concept", content, ("company_name", "positioning", "messaging", "launch_narrative"))


def _product_screen(tokens: dict[str, Any], screen: dict[str, str]) -> str:
    c = tokens["company"]
    esc = html.escape
    fake_rows = "".join(f"<div class=\"card\"><span class=\"fictional\">Sample interface content</span><h3>{esc(p['title'])}</h3><p>{esc(p['message'])}</p></div>" for p in tokens["messaging_pillars"])
    content = (
        f"<main class=\"wrap\"><section class=\"hero\"><span class=\"fictional\">Fictional product UI</span><h1>{esc(screen['title'])}</h1>"
        f"<p class=\"lede\">{esc(screen['purpose'])}</p><div class=\"surface\"><strong>{esc(c['product_name'])}</strong><p>{esc(c['tagline'])}</p></div></section>"
        f"<section><h2>Team workspace</h2><div class=\"grid\">{fake_rows}</div></section></main>"
    )
    return _html_shell(tokens, screen["title"] + " | Fictional product UI", content, ("product_story", "messaging"))


def _diagram(tokens: dict[str, Any], workflow: bool) -> str:
    colors = tokens["palette"]
    font = tokens["typography"]["body"]["family"]
    if workflow:
        labels = (("Listen", "Bring feedback together"), ("Group", "Keep related context"), ("Decide", "Choose a next step"))
        title = "How the fictional workflow works"
        start_x = 65
        gap = 250
        nodes = []
        for i, (head, sub) in enumerate(labels):
            x = start_x + i * gap
            nodes.append(f"<rect x=\"{x}\" y=\"150\" width=\"190\" height=\"130\" rx=\"14\" fill=\"{colors['muted']}\" stroke=\"{colors['primary']}\" stroke-width=\"3\"/><text x=\"{x + 18}\" y=\"200\" fill=\"{colors['primary']}\" font-family=\"{font}\" font-size=\"23\">{head}</text><text x=\"{x + 18}\" y=\"235\" fill=\"{colors['ink']}\" font-family=\"{font}\" font-size=\"13\">{sub}</text>")
            if i < 2:
                nodes.append(f"<path d=\"M{x + 196} 215 H{x + 238}\" stroke=\"{colors['accent']}\" stroke-width=\"5\"/><path d=\"M{x + 229} 206 L{x + 240} 215 L{x + 229} 224\" fill=\"none\" stroke=\"{colors['accent']}\" stroke-width=\"4\"/>")
        body = f"<rect width=\"800\" height=\"480\" fill=\"{colors['paper']}\"/><text x=\"40\" y=\"70\" fill=\"{colors['ink']}\" font-family=\"{tokens['typography']['heading']['family']}\" font-size=\"28\">How it works</text>{''.join(nodes)}{_base_svg_text(tokens)}"
    else:
        title = "Fictional product architecture"
        rows = (("Inputs", "Notes, conversations, requests"), (tokens["company"]["product_name"], "Organize themes and context"), ("Outputs", "Visible choices and next steps"))
        nodes = []
        for i, (head, sub) in enumerate(rows):
            y = 105 + i * 100
            fill = colors["muted"] if i != 1 else colors["primary"]
            text_fill = colors["ink"] if i != 1 else colors["paper"]
            nodes.append(f"<rect x=\"170\" y=\"{y}\" width=\"460\" height=\"72\" rx=\"10\" fill=\"{fill}\"/><text x=\"195\" y=\"{y + 30}\" fill=\"{text_fill}\" font-family=\"{font}\" font-size=\"20\">{html.escape(head)}</text><text x=\"195\" y=\"{y + 54}\" fill=\"{text_fill}\" font-family=\"{font}\" font-size=\"13\">{html.escape(sub)}</text>")
            if i < 2:
                nodes.append(f"<path d=\"M400 {y + 74} V{y + 96}\" stroke=\"{colors['accent']}\" stroke-width=\"4\"/>")
        body = f"<rect width=\"800\" height=\"480\" fill=\"{colors['paper']}\"/><text x=\"40\" y=\"60\" fill=\"{colors['ink']}\" font-family=\"{tokens['typography']['heading']['family']}\" font-size=\"28\">Product architecture</text>{''.join(nodes)}{_base_svg_text(tokens)}"
    return _svg(tokens, title, body, ("product_story", "messaging"))


def _article(tokens: dict[str, Any]) -> str:
    c = tokens["company"]
    p = tokens["messaging_pillars"]
    body = f"""# {c['name']} is a fictional concept for a clearer path through product feedback

> {c['tagline']}

**Fictional launch article.** This concept describes an imagined product and makes no claims about real customers, adoption, or results.

Teams can collect thoughtful feedback in many places and still struggle to decide what deserves attention. {c['positioning']} The idea is simple: make the context easier to carry from an observation to a decision.

## A clear place to start

{p[0]['message']} A practical workflow begins with listening, then groups related notes so a team can discuss the underlying need.

## Keep the reason close

{p[1]['message']} {p[2]['message']} The goal is a thoughtful record of how a choice was made, not a promise that every request will be built.

## An invitation to explore

{c['product_name']} is a fictional product direction from {c['name']}. It is designed around a clear question: what is the next useful step, and what context should travel with it?

The launch story follows the messaging decision recorded in `reasoning.json` under `messaging` and `launch_narrative`.
"""
    return _markdown(tokens, body, ("positioning", "messaging", "launch_narrative"))


def _deck(tokens: dict[str, Any]) -> str:
    c = tokens["company"]
    p = tokens["messaging_pillars"]
    slide_data = [
        ("A clearer path through feedback", c["tagline"]),
        ("The everyday tension", "Useful observations arrive in different places, with context attached."),
        ("The idea", c["positioning"]),
        ("A simple workflow", "Listen, group, and make a considered next step visible."),
        (p[0]["title"], p[0]["message"]),
        (p[1]["title"], p[1]["message"]),
        (p[2]["title"], p[2]["message"]),
        ("Product concept", f"{c['product_name']} brings an inbox, themes, and a decision board into one imagined workspace."),
        ("A launch that teaches", "Show the workflow with clear examples and invite teams to explore the concept."),
        ("Open questions", "Learn which sources, team habits, and decision records would be most useful to support."),
    ]
    slides = []
    for index, (heading, copy) in enumerate(slide_data, start=1):
        slides.append(f"<section class=\"slide\"><div class=\"slide-top\"><span>{index:02d} / FICTIONAL CONCEPT</span><span>{html.escape(c['name'])}</span></div><div><p class=\"fictional\">Fictional investor deck concept</p><h1>{html.escape(heading)}</h1><p class=\"lede\">{html.escape(copy)}</p></div><div class=\"slide-bottom\">{html.escape(c['tagline'])}</div></section>")
    css = ".slide{min-height:92vh;padding:7vh 8vw;display:flex;flex-direction:column;justify-content:space-between;border-bottom:1px solid var(--color-muted);page-break-after:always}.slide h1{max-width:850px;font-family:\"" + tokens["typography"]["display"]["family"] + "\";font-size:clamp(38px,7vw,76px)}.slide-top,.slide-bottom{display:flex;justify-content:space-between;font-size:12px;letter-spacing:.08em}.slide .lede{max-width:760px;font-size:clamp(18px,2.5vw,26px)}@media print{body{background:var(--color-paper)}.slide{min-height:100vh}}"
    return _html_shell(tokens, c["name"] + " | Fictional investor deck", "<main>" + "".join(slides) + "</main>", ("positioning", "messaging", "product_story", "campaign"), css)


def _social(tokens: dict[str, Any], kind: str) -> str:
    c = tokens["company"]
    colors = tokens["palette"]
    if kind == "launch":
        heading, copy, ref = c["tagline"], c["positioning"], "launch_narrative"
    elif kind == "feature":
        heading, copy, ref = tokens["messaging_pillars"][0]["title"], tokens["messaging_pillars"][0]["message"], "messaging"
    else:
        heading, copy, ref = "Keep the reason close", tokens["messaging_pillars"][2]["message"], "messaging"
    font = tokens["typography"]["heading"]["family"]
    body = (
        f"<rect width=\"800\" height=\"480\" fill=\"{colors['paper']}\"/><rect x=\"28\" y=\"28\" width=\"744\" height=\"424\" rx=\"18\" fill=\"none\" stroke=\"{colors['primary']}\" stroke-width=\"3\"/>"
        f"<text x=\"62\" y=\"82\" fill=\"{colors['primary']}\" font-family=\"{tokens['typography']['mono']['family']}\" font-size=\"13\" letter-spacing=\"2\">FICTIONAL SOCIAL CONCEPT</text>"
        f"<text x=\"62\" y=\"175\" fill=\"{colors['ink']}\" font-family=\"{font}\" font-size=\"38\">{html.escape(heading)}</text>"
        f"<foreignObject x=\"62\" y=\"205\" width=\"660\" height=\"150\"><div xmlns=\"http://www.w3.org/1999/xhtml\" style=\"font-family:'{tokens['typography']['body']['family']}';font-size:20px;color:{colors['ink']}\">{html.escape(copy)}</div></foreignObject>"
        f"<text x=\"62\" y=\"404\" fill=\"{colors['primary']}\" font-family=\"{tokens['typography']['body']['family']}\" font-size=\"16\">{html.escape(c['name'])} | {html.escape(c['tagline'])}</text>"
    )
    return _svg(tokens, f"Fictional social asset: {kind}", body, (ref, "company_name"), "800 480")


def _ad(tokens: dict[str, Any], index: int) -> str:
    pillar = tokens["messaging_pillars"][index]
    c = tokens["company"]
    colors = tokens["palette"]
    body = (
        f"<rect width=\"800\" height=\"480\" fill=\"{colors['paper']}\"/><path d=\"M0 0 H800 V120 H0 Z\" fill=\"{colors['primary']}\"/>"
        f"<text x=\"42\" y=\"54\" fill=\"{colors['paper']}\" font-family=\"{tokens['typography']['mono']['family']}\" font-size=\"13\" letter-spacing=\"2\">FICTIONAL AD CONCEPT</text>"
        f"<text x=\"42\" y=\"190\" fill=\"{colors['ink']}\" font-family=\"{tokens['typography']['heading']['family']}\" font-size=\"34\">{html.escape(pillar['title'])}</text>"
        f"<foreignObject x=\"42\" y=\"220\" width=\"680\" height=\"110\"><div xmlns=\"http://www.w3.org/1999/xhtml\" style=\"font-family:'{tokens['typography']['body']['family']}';font-size:19px;color:{colors['ink']}\">{html.escape(pillar['message'])}</div></foreignObject>"
        f"<text x=\"42\" y=\"390\" fill=\"{colors['primary']}\" font-family=\"{tokens['typography']['body']['family']}\" font-size=\"16\">Pillar: {html.escape(pillar['id'])}</text>"
        f"<text x=\"42\" y=\"425\" fill=\"{colors['ink']}\" font-family=\"{tokens['typography']['body']['family']}\" font-size=\"14\">{html.escape(c['name'])} | {html.escape(c['tagline'])}</text>"
    )
    return _svg(tokens, f"Fictional ad concept for {pillar['id']}", body, ("messaging", "campaign"), "800 480")


def generate_artifacts(tokens: dict[str, Any]) -> dict[str, str]:
    """Render all package artifacts from token and reasoning references."""
    c = tokens["company"]
    artifacts: dict[str, str] = {
        "visual/mark.svg": _logo(tokens),
        "visual/color-system.svg": _color_sheet(tokens),
        "visual/typography-specimen.svg": _type_specimen(tokens),
        "web/landing-page.html": _landing(tokens),
        "diagrams/product-architecture.svg": _diagram(tokens, False),
        "diagrams/how-it-works.svg": _diagram(tokens, True),
        "editorial/launch-article.md": _article(tokens),
        "deck/investor-deck.html": _deck(tokens),
        "social/launch-announcement.svg": _social(tokens, "launch"),
        "social/feature-card.svg": _social(tokens, "feature"),
        "social/quote-card.svg": _social(tokens, "quote"),
        "video/storyboard.md": _storyboard(tokens),
        "campaign/launch-plan.md": _campaign(tokens),
        "docs/brand-guide.md": _brand_guide(tokens),
        "ads/ad-variants.md": _ad_copy(tokens),
    }
    for screen in tokens["product"]["screens"]:
        artifacts[f"product/{screen['id']}.html"] = _product_screen(tokens, screen)
    for index in range(3):
        artifacts[f"ads/ad-{index + 1:02d}.svg"] = _ad(tokens, index)
    return dict(sorted(artifacts.items()))


def _storyboard(tokens: dict[str, Any]) -> str:
    c = tokens["company"]
    shots = [
        ("Opening", "A tidy desk and a handful of notes appear.", f"{c['tagline']}."),
        ("Gather", "Notes move into a calm fictional inbox.", "Start by bringing the useful feedback together."),
        ("Connect", "Related notes settle into a shared theme.", "Keep the context close as patterns take shape."),
        ("Decide", "A decision card links a next step to its source notes.", "Choose a practical next step and leave the reasoning visible."),
        ("Close", f"The {c['name']} wordmark appears with a fictional concept label.", "A clear path through the work, one thoughtful decision at a time."),
    ]
    rows = "\n".join(f"| {index:02d} | {name} | {visual} | {narration} |" for index, (name, visual, narration) in enumerate(shots, 1))
    body = f"""# Fictional video storyboard

This is a fictional production concept. The scenes describe a mock interface, not recorded product footage.

| Shot | Scene | Visual direction | Narration |
| --- | --- | --- | --- |
{rows}

## Production notes

- Build every frame from the brand palette and type scale.
- Use generated SVG and HTML interface elements only.
- Keep narration clear, practical, and thoughtful.
"""
    return _markdown(tokens, body, ("visual_identity", "product_story", "launch_narrative"))


def _campaign(tokens: dict[str, Any]) -> str:
    c = tokens["company"]
    body = f"""# Fictional launch campaign plan

This plan belongs to an imagined company and describes a proposed campaign, not completed activity or measured results.

## Campaign idea

{c['tagline']}. Use a clear, practical walkthrough to show how feedback can move into a considered decision.

## Phases

| Phase | Activity | Channel | Creative |
| --- | --- | --- | --- |
| Prepare | Introduce the problem and collect team questions | Owned site, newsletter draft | Launch article and landing page |
| Explain | Show how notes become themes and next steps | Product walkthrough, social posts | Storyboard, feature cards, ad concepts |
| Invite | Ask readers to explore the fictional product concept | Owned site, community discussion | Landing page and campaign note |

## Channel plan

- Owned: publish the launch article and an accessible landing page.
- Social: adapt the generated announcement, feature, and quote cards.
- Video: narrate the storyboard with a calm, thoughtful voice.
- Conversation: use open questions to learn what context teams want to preserve.

All sample materials are fictional. No reach, conversion, revenue, or customer figures are asserted.
"""
    return _markdown(tokens, body, ("messaging", "launch_narrative", "campaign"))


def _brand_guide(tokens: dict[str, Any]) -> str:
    c = tokens["company"]
    palette_rows = "\n".join(f"| {key} | `{value}` |" for key, value in tokens["palette"].items())
    type_rows = "\n".join(f"| {role} | {style['family']} | {style['size_px']} px |" for role, style in tokens["typography"].items())
    pillar_rows = "\n".join(f"- **{p['title']}:** {p['message']}" for p in tokens["messaging_pillars"])
    body = f"""# Fictional brand guide: {c['name']}

**Fictional concept.** {c['tagline']}

## Positioning

{c['positioning']}

## Messaging pillars

{pillar_rows}

## Color tokens

| Role | Token |
| --- | --- |
{palette_rows}

## Typography tokens

| Role | Family | Size |
| --- | --- | --- |
{type_rows}

## Mark

The generated mark uses the `{tokens['logo']['concept']}` concept with {tokens['logo']['unit_count']} units and a {tokens['logo']['rotation_degrees']} degree rotation.

## Traceability

Token version: `{tokens['schema_version']}`. Key decisions are recorded in the adjacent `reasoning.json` file. This fictional guide and its generated SVG and HTML visuals are design concepts only.
"""
    return _markdown(tokens, body, ("company_name", "positioning", "messaging", "visual_identity"))


def _ad_copy(tokens: dict[str, Any]) -> str:
    rows = "\n".join(f"| Ad {index + 1} | `{pillar['id']}` | {pillar['title']} | {pillar['message']} |" for index, pillar in enumerate(tokens["messaging_pillars"]))
    body = f"""# Fictional ad concepts

These sample concepts are fictional. Each line is tagged with the messaging pillar it expresses.

| Variant | Pillar ID | Headline | Copy |
| --- | --- | --- | --- |
{rows}
"""
    return _markdown(tokens, body, ("messaging", "campaign"))

