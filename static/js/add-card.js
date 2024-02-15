/**
 * Script for Add Card page
 */

class AddCardPage {
    constructor() {
        this.nameInput = document.querySelector('#nameInput');
        this.dataList = document.querySelector('#nameListOptions');
        this.dataBody = document.querySelector('#dataBody');
        this.dataError = document.querySelector('#dataError');
        this.dataLoading = document.querySelector('#dataLoading');
        this.form = document.querySelector('#nameSearchForm');
        this.cardTableBody = document.querySelector('#cardTableBody');
        this.cardImageEl = document.querySelector('#cardImage');

        this.utilities = new Utilities();

        this.focusNameInput();
        this.setupInputListener();
        this.setupSubmitListener();
    }

    throwError(error) {
        this.dataError.innerText = error;
        this.dataBody.hidden = true;
        this.dataError.hidden = false;
        this.dataLoading.hidden = true;
    }

    focusNameInput() {
        this.nameInput.focus();
    }

    setupInputListener() {
        this.nameInput.addEventListener('input', () => {
            if (this.nameInput.value.length > 1) {
                fetch(`https://api.scryfall.com/cards/autocomplete?q=${this.nameInput.value}`)
                    .then(res => res.json())
                    .then(data => {
                        this.dataList.innerHTML = '';
                        if (data?.data?.length > 0) {
                            data.data.forEach(card => {
                                const option = document.createElement('option');
                                option.value = card;
                                this.dataList.appendChild(option);
                            });
                        }
                    });
            }
        });
    }

    showLoadingScreen() {
        this.dataBody.hidden = true;
        this.dataError.hidden = true;
        this.dataLoading.hidden = false;
    }

    hideLoadingScreen() {
        this.dataBody.hidden = false;
        this.dataError.hidden = true;
        this.dataLoading.hidden = true;
    }

    buildDataScreen(data) {
        this.cardTableBody.innerHTML = '';

        // Create table row for each card printing
        data.forEach(card => {
            if (card?.games?.includes("paper")) {
                const row = document.createElement('tr');
                const setIdCell = document.createElement('td');
                const collectorNumberCell = document.createElement('td');
                const rarityCell = document.createElement('td');
                const regularPriceCell = document.createElement('td');
                const foilPriceCell = document.createElement('td');
                const addToCollectionCell = document.createElement('td');
                const addToCollectionFoilCell = document.createElement('td');

                row.dataset.scryfallId = card?.id;

                setIdCell.classList.add('text-uppercase');
                rarityCell.classList.add('text-capitalize');
                addToCollectionCell.classList.add('text-center');
                addToCollectionFoilCell.classList.add('text-center');
                
                setIdCell.innerText = card?.set;
                collectorNumberCell.innerText = card?.collector_number;
                rarityCell.innerText = card?.rarity;
                regularPriceCell.innerText = card?.prices?.usd ? `$${card.prices.usd}` : ''
                foilPriceCell.innerText = card?.prices?.usd_foil ? `$${card.prices.usd_foil}` : ''
                addToCollectionCell.innerHTML = `
                    <a href="/card/add/${card.id}" data-bs-toggle="tooltip" data-bs-title="Add Regular to Collection">
                        <i class="bi-plus-circle-fill"></i>
                    </a>
                `;
                addToCollectionFoilCell.innerHTML = `
                    <a href="/card/add/${card.id}?foil=true" data-bs-toggle="tooltip" data-bs-title="Add Foil to Collection">
                        <i class="bi-brightness-high-fill"></i>
                    </a>
                `;

                row.appendChild(setIdCell);
                row.appendChild(collectorNumberCell);
                row.appendChild(rarityCell);
                row.appendChild(regularPriceCell);
                row.appendChild(foilPriceCell);
                row.appendChild(addToCollectionCell);
                row.appendChild(addToCollectionFoilCell);
                this.cardTableBody.appendChild(row);
            }
        });
    }

    addDynamicImageEventListeners() {
        const rows = document.querySelectorAll('[data-scryfall-id]');
        this.cardImageEl.src = `https://api.scryfall.com/cards/${rows[0].dataset.scryfallId}?format=image`;
        this.utilities.enableDynamicCardImages(rows, this.cardImageEl);
    }

    setupSubmitListener() {
        this.form.addEventListener('submit', (e) => {
            e.preventDefault();
            e.stopPropagation();

            this.nameInput.blur();
            this.showLoadingScreen();

            if (this.nameInput.value.length > 1) {
                fetch(`https://api.scryfall.com/cards/named?fuzzy=${this.nameInput.value}`)
                    .then(res => res.json())
                    .then(data => {
                        if (data?.prints_search_uri) {
                            fetch(data.prints_search_uri)
                                .then(res => res.json())
                                .then(data => {
                                    if (data?.data?.length > 0) {
                                        this.buildDataScreen(data.data);
                                        this.addDynamicImageEventListeners();
                                        this.utilities.enableTooltips();
                                        this.hideLoadingScreen();
                                    } else {
                                        this.throwError("Error loading card printings")
                                    }
                                });
                        } else {
                            this.throwError("Could not find a card by that name")
                        }
                    });
            } else {
                this.throwError("A search must have more than 2 characters");
            }
        });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new AddCardPage();
});
