/**
 * Script for Deck Gather Page
 */

class DeckGatherPage {
    constructor() {
        this.rows = document.querySelectorAll('[data-scryfall-id]');
        this.cardImageEl = document.querySelector('#cardImage');

        this.utilities = new Utilities();

        this.utilities.enableDynamicCardImages(this.rows, this.cardImageEl);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new DeckGatherPage();
});
