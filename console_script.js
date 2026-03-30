let urls = [];
document.querySelectorAll('a').forEach(link => {
    let href = link.href;
    if (href.includes('commonsense.org/node/')) {
        if (href.includes('/url?q=')) {
            href = href.split('/url?q=')[1].split('&')[0];
        }
        href = href.split('#')[0];
        if (!urls.includes(href)) {
            urls.push(href);
        }
    }
});
console.log(urls.join('\n'));
copy(urls.join('\n'));
console.log(`Found ${urls.length} unique URLs - copied to clipboard!`);
