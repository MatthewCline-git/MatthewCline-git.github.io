---
layout: page
title: Essays
permalink: /essays/
---

# Essay Collection

Below is a chronological collection of my essays. Click on any title to read the full piece.

{% assign sorted_posts = site.posts | sort: 'date' | reverse %}
{% for post in sorted_posts %}

## [{{ post.title }}]({{ post.url | relative_url }})

_{{ post.date | date: "%B %d, %Y" }}_

{% if post.description %}
{{ post.description }}
{% else %}
{{ post.excerpt | strip_html | truncatewords: 30 }}
{% endif %}

[Read more]({{ post.url | relative_url }})

---

{% endfor %}
