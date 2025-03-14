How I Built this Website
Web Development
2025-03-05
work.avif
Learn how I built my website from scratch! From choosing the tech stack to deploying it, I’ll walk you through the process, challenges, and key decisions. Whether you're a developer or just curious, get insights into web development, design, and optimization.

## Introduction

I wanted to make a website so that I could market myself and share my expertise. This required the website to be fast to load and search engine friendly. Another constraint I had was that I did not want an over-engineered solution that is costly to maintain and deploy. The website needed to be built as fast as possible in technologies I was already familiar with. With all this in mind, it was established that I need a static website.

## Possible Tech Stacks and What I Chose

I could have made the website quickly in WordPress. It would have been easy to setup and I could have easily leveraged a large ecosystem of plugins to enhance my website's functionality. I decided against WordPress because it still requires a backend, and I lose out on the ability to customize with native web technologies without going through a lot of hoops. Secondly, it introduces dependencies on third parties which requires constant upkeep.

React / Next.js / Tailwind would have been overkill for this simple use case. So would have introducing a backend framework such as Django / Laravel just used to use the templating engine.

## My Solution

I chose to make use of the fundamentals, utilizing as many modern HTML/CSS features as I could to reduce my dependency on JavaScript. To avoid duplication of code, I used Jinja2 templates. I wrote a Python script that generates my pages, adding in images, canonicals, and meta descriptions where needed. The blogs are stored in markdown, and code is organized into templates.

I used JavaScript for the search functionality and one external library mini-search.js which itself does not have any external dependencies. I vendorized this dependency, meaning I serve it along with all the other assets of my website.

## Tech Stack Summary

- HTML
- CSS
- Python (Jinja2)
- JavaScript (mini-search.js)

## Hosting

For hosting I used GitHub Pages. I just push my build code into the root directory of my repository and it is ready to be served. GitHub takes care of the HTTPS certificates and load balancing.
