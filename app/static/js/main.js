/**
 * Lotus Main Javascript
 */

class Utilities {
    enableTooltips() {
        const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
        [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    }

    enableDynamicCardImages(rows, cardImageEl) {
        if (rows.length > 0 && cardImageEl != null) {
            // Set first image if needed
            cardImageEl.src = `https://api.scryfall.com/cards/${rows[0].dataset.scryfallId}?format=image`;

            // Then handle each row
            rows.forEach(row => {
                row.addEventListener('mouseover', () => {
                    cardImageEl.src = `https://api.scryfall.com/cards/${row.dataset.scryfallId}?format=image`;
                });
            });
        }
    }

    async livePriceLoading(rows) {
        let totalPrice = 0;

        for (const row of rows) {
            await fetch(`https://api.scryfall.com/cards/${row.dataset.scryfallId}`)
                .then(res => res.json())
                .then(data => {
                    const priceEl = row.querySelector('.js-price');
                    const foilEl = row.querySelector('.js-foil');
                    if (foilEl.innerText.toLowerCase() === 'regular' && data.prices.usd) {
                        totalPrice += parseFloat(data['prices']['usd']);
                        priceEl.innerText = `$${data['prices']['usd']}`;
                    } else if (data?.prices?.usd_foil) {
                        totalPrice += parseFloat(data['prices']['usd_foil']);
                        priceEl.innerText = `$${data['prices']['usd_foil']}`;
                    } else if (data?.prices?.usd_etched) {
                        totalPrice += parseFloat(data['prices']['usd_etched']);
                        priceEl.innerText = `$${data['prices']['usd_etched']}`;
                    }
                });
        }

        return totalPrice;
    }

    async postDataToAPI(endpoint, body, errorToastBody, errorToast, successToastBody, successToast) {
        const options = {
            method: "POST",
            body: body
        }

        const res = await fetch(endpoint, options);
        const data = await res.json();

        const success = data?.success;
        const error = data?.error;

        if (error) {
            errorToastBody.innerText = error;
            errorToast.show();
            return false;
        } else if (success) {
            successToastBody.innerHTML = success;
            successToast.show();
            return true;
        }
    }
}

class Navbar {
    constructor() {
        this.searchInput = document.querySelector('#searchInput');
        this.dataList = document.querySelector('#searchListOptions');
        
        this.setupKeyboardListener();
        this.setupInputListener();        
    }

    setupKeyboardListener() {
        document.addEventListener('keydown', (e) => {
            if (e.metaKey && e.keyCode === 191) {
                this.searchInput.focus();
            }
        });
    }

    setupInputListener() {
        this.searchInput.addEventListener('input', () => {
            if (this.searchInput.value.length > 2) {
                const form = new FormData();
                form.append("query", this.searchInput.value);
                fetch("/api/cards/autocomplete", { method: 'POST', body: form })
                    .then(res => res.json())
                    .then(data => {
                        this.dataList.innerHTML = '';
                        if (data.length > 0) {
                            data.forEach(cardName => {
                                const option = document.createElement('option');
                                option.value = cardName;
                                this.dataList.appendChild(option);
                            });
                        }
                    });
            }
        });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new Navbar();
    const utilities = new Utilities();
    utilities.enableTooltips();
});
