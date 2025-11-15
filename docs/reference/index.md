---
layout: default
title: Reference
nav_order: 3
permalink: /reference/
---

# Reference Library

Authoritative specs, architecture notes, and generated man pages for the Claude CTX CLI.

## Architecture Notes

{% assign reference_pages = site.pages | sort: "path" %}
<ul class="doc-list">
{% for ref in reference_pages %}
  {% unless ref.path contains "reference/" %}
    {% continue %}
  {% endunless %}
  {% if ref.path == "reference/index.md" %}
    {% continue %}
  {% endif %}
  {% unless ref.path contains ".md" %}
    {% continue %}
  {% endunless %}
  {% assign heading_line = "" %}
  {% assign lines = ref.content | split: "\n" %}
  {% for line in lines %}
    {% assign stripped = line | strip %}
    {% unless stripped == "" %}
      {% assign heading_line = stripped %}
      {% break %}
    {% endunless %}
  {% endfor %}
  {% assign heading_line = heading_line | replace: "#", "" | strip %}
  {% assign fallback = ref.name | replace: ".md", "" | replace: "-", " " | replace: "_", " " %}
  {% assign display_title = heading_line | default: fallback | strip %}
  <li>
    <a href="{{ ref.url | relative_url }}">{{ display_title }}</a>
    <span class="muted">({{ ref.path }})</span>
  </li>
{% endfor %}
</ul>

## CLI Man Pages

{% assign static_files = site.static_files | sort: "path" %}
<ul>
{% for page in static_files %}
  {% unless page.path contains "/reference/" %}
    {% continue %}
  {% endunless %}
  {% unless page.extname == ".1" %}
    {% continue %}
  {% endunless %}
  <li>
    <a href="{{ page.path | relative_url }}">{{ page.name }}</a>
    <span class="muted">Use `man {{ page.name | replace: '.1', '' }}` locally.</span>
  </li>
{% endfor %}
</ul>
