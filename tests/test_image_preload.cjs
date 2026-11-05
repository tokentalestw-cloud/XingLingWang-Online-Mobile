const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname, '../static/game_v8.js'), 'utf8');
const start = source.indexOf('const _xlwPreloadedImageUrls');
const end = source.indexOf('// ===== 線上雙人對戰網路狀態', start);
const images = [];
const scope = {
  LITTLE_TRAVELER: { image: '/traveler.jpeg' },
  Image: class {
    constructor() { images.push(this); }
    decode() { throw Error('Bulk decoding should not be forced'); }
  }
};
vm.createContext(scope);
vm.runInContext(source.slice(start, end), scope);
scope.preloadCommonCardsIdle(Array.from({ length: 1500 }, (_, i) => ({ image: '/catalog-' + i })));
assert.equal(images.length, 2);
scope.preloadCardImages(Array.from({ length: 20 }, (_, i) => ({ image: '/deck-' + i })));
assert.equal(images.length, 3);
images[0].onload();
assert.equal(images.length, 4);
assert.equal(images[3].src, '/deck-1');
images[0].onload();
assert.equal(images.length, 4, 'Repeated callbacks cannot free another load slot');
images[1].onerror();
assert.equal(images.length, 5);
scope.preloadCardImages([{ image: '/deck-0' }]);
assert.equal(images.length, 5, 'An already queued URL must not be requested twice');
let completed = 2;
while (completed < images.length) images[completed++].onload();
assert.equal(images.length, 23);
scope.preloadCardImages([{ image: '/traveler.jpeg' }]);
assert.equal(images.length, 23);
assert.equal(images.filter(image => image.src === '/traveler.jpeg').length, 2, 'Failed images remain retryable');
console.log('8 catalogue suppression, three-load limit, priority, deduplication, callback and retry checks: PASS');
