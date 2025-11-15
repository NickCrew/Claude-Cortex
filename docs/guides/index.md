---
layout: default
title: Guides
nav_order: 2
permalink: /guides/
---

# Product Guides

Browse every published guide in one place. Use the filters below or tap a title to open the article.

{% assign guide_pages = site.pages | where_exp: "p", "p.path contains 'guides/'" | sort: "path" %}
<div class="doc-grid">
{% for guide in guide_pages %}
  {% if guide.path == "guides/index.md" %}
    {% continue %}
  {% endif %}
  {% assign heading_line = "" %}
  {% assign lines = guide.content | split: "\n" %}
  {% for line in lines %}
    {% assign stripped = line | strip %}
    {% unless stripped == "" %}
      {% assign heading_line = stripped %}
      {% break %}
    {% endunless %}
  {% endfor %}
  {% assign heading_line = heading_line | replace: "#", "" | strip %}
  {% assign fallback = guide.name | replace: ".md", "" | replace: ".markdown", "" | replace: "-", " " | replace: "_", " " %}
  {% assign display_title = heading_line | default: fallback | strip %}
  <a class="doc-card" href="{{ guide.url | relative_url }}">
    <h3>{{ display_title }}</h3>
    <p class="muted">
      {{ guide.path | replace: "guides/", "" | replace: ".md", "" }}
    </p>
    <span class="doc-card__arrow">Read →</span>
  </a>
{% endfor %}
</div>
