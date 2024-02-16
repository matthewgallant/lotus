/**
 * Script for Deck Page
 */

class DeckPage {
    constructor() {
        this.totalPrice = 0;
        this.priceBadgeEl = document.querySelector('.js-priceBadge');
        this.rows = document.querySelectorAll('[data-scryfall-id]');
        this.cardImageEl = document.querySelector('#cardImage');

        this.utilities = new Utilities();

        this.utilities.enableDynamicCardImages(this.rows, this.cardImageEl);
        this.getPricingData();
    }

    async getPricingData() {
        this.totalPrice = await this.utilities.livePriceLoading(this.rows);
        this.priceBadgeEl.innerText = `$${Math.round((this.totalPrice + Number.EPSILON) * 100) / 100}`;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new DeckPage();
});
