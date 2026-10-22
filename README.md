# LMM Best

The open-source project directory for [TokenNotIncluded](https://github.com/TokenNotIncluded), hosted at **https://lmm.best/**.

LMM Best originally means **“最好的多模态大语言模型” — the best large multimodal model**. The name expresses an aspiration; today the site introduces the organization's open-source AI infrastructure and applications.

## Preview

```sh
python3 -m http.server 8080 --directory site
```

Open http://localhost:8080/. The site is plain HTML and CSS, with no build step, JavaScript, analytics, or external runtime assets. It supports small screens, dark mode, keyboard navigation and reduced motion.

## Deploy

Serve the contents of `site/` from `/var/www/lmm.best/current`. Install `deploy/nginx.conf` in the host's Nginx configuration after reviewing its listeners and obtaining a certificate for `lmm.best` with the webroot `/var/lib/letsencrypt`. Validate with `nginx -t` before reloading. Keep the previous release directory for rollback.

For initial certificate issuance, activate only the HTTP server block, obtain the certificate, then activate the complete configuration. Never copy another hostname's certificate or private key.

Submit `https://lmm.best/sitemap.xml` to Google Search Console. The sitemap lists only the canonical homepage; linked projects maintain their own sitemaps.

## Credits and license

MIT. The organization logo is from [TokenNotIncluded/.github](https://github.com/TokenNotIncluded/.github/blob/main/assets/logo.png). Organization copy follows its [public profile](https://github.com/TokenNotIncluded/.github/blob/main/profile/README.md). Project links point to their respective websites and repositories; each project has its own license.
