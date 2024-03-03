/**
 * Script for Card Page
 */

class CardPage {
    constructor() {
        this.rows = document.querySelectorAll('[data-scryfall-id]');
        this.cardImageEl = document.querySelector('#cardImage');

        this.utilities = new Utilities();

        this.utilities.enableDynamicCardImages(this.rows, this.cardImageEl);
        this.utilities.livePriceLoading(this.rows);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new CardPage();
});
