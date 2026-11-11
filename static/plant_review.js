'use strict';

function element(tag, content, className) {
    const node = document.createElement(tag);
    node.textContent = content;
    if (className) node.className = className;
    return node;
}

async function loadCards() {
    const status = document.querySelector('#status');
    try {
        const response = await fetch('plant_review.json');
        if (!response.ok) throw new Error(response.status);
        const {cards} = await response.json();
        const fragments = document.createDocumentFragment();
        for (const card of cards) {
            const tile = element('article', '');
            const imageLink = element('a', '');
            imageLink.href = card.image;
            const image = element('img', '');
            image.src = card.image;
            image.alt = card.name + '卡圖';
            image.loading = 'lazy';
            imageLink.append(image);

            const details = element('div', '');
            details.append(element('h2', card.name));
            details.append(element('p', [card.id, card.edition, card.kind].filter(Boolean).join(' · '), 'meta'));
            const rules = element('ul', '');
            for (const line of card.interpretation) rules.append(element('li', line));
            details.append(rules);
            if (card.review_note) details.append(element('p', card.review_note, 'meta'));
            const source = element('a', '官網卡牌詳情');
            source.href = card.source_url;
            details.append(source);
            tile.append(imageLink, details);
            fragments.append(tile);
        }
        document.querySelector('#cards').append(fragments);
        status.textContent = '共 ' + cards.length + ' 筆卡圖。';
    } catch (error) {
        status.textContent = '無法載入植物園審閱資料。';
        console.error(error);
    }
}

loadCards();
