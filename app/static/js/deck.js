/**
 * Script for Deck Page
 */

class DeckPage {
    constructor() {
        this.totalPrice = 0;
        this.priceBadgeEl = document.querySelector('.js-priceBadge');
        this.mainboardRows = document.querySelectorAll('#mainboard-tab-pane [data-scryfall-id]');
        this.sideboardRows = document.querySelectorAll('#sideboard-tab-pane [data-scryfall-id]');
        this.mainboardCardImageEl = document.querySelector('#mainboardCardImage');
        this.sideboardCardImageEl = document.querySelector('#sideboardCardImage');

        this.utilities = new Utilities();

        this.utilities.enableDynamicCardImages(this.mainboardRows, this.mainboardCardImageEl);
        this.utilities.enableDynamicCardImages(this.sideboardRows, this.sideboardCardImageEl);
        this.getPricingData();
    }

    async getPricingData() {
        this.totalPrice = await this.utilities.livePriceLoading(this.mainboardRows);
        this.priceBadgeEl.innerText = `$${(Math.round((this.totalPrice + Number.EPSILON) * 100) / 100).toFixed(2)}`;

        // Load sideboard prices after mainboard
        await this.utilities.livePriceLoading(this.sideboardRows);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new DeckPage();
});
