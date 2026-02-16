// Common Sense Review URL Extractor
// NET Lab, Inc. | February 2026
// 
// HOW TO USE:
// 1. Search Google: site:commonsense.org/node "community review of [PRODUCT]"
// 2. Click "repeat the search with the omitted results included"
// 3. Open Safari Developer Console: Cmd + Option + C
// 4. Copy/paste this entire script and press Enter
// 5. URLs are automatically copied to clipboard
// 6. Paste into TextEdit, repeat for additional pages

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
