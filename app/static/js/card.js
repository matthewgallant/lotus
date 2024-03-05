/**
 * Script for Card Page
 */

class CardPage {
    constructor() {
        this.rows = document.querySelectorAll('[data-scryfall-id]');
        this.cardImageEl = document.querySelector('#cardImage');
        this.quantityModals = document.querySelectorAll('.js-quantityModal');
        this.successToast = bootstrap.Toast.getOrCreateInstance(document.querySelector('#successToast'));
        this.successToastBody = document.querySelector('#successToast .js-toastBody');
        this.errorToast = bootstrap.Toast.getOrCreateInstance(document.querySelector('#errorToast'));
        this.errorToastBody = document.querySelector('#errorToast .js-toastBody');

        this.utilities = new Utilities();

        this.utilities.enableDynamicCardImages(this.rows, this.cardImageEl);
        this.utilities.livePriceLoading(this.rows);
        this.setupRowActionEventListeners();
        this.setupQuantityModalEventListeners();
    }

    setupRowActionEventListeners() {
        this.rows.forEach(row => {
            const addButtons = row.querySelectorAll(".js-addButton");
            const deleteButton = row.querySelector(".js-deleteButton");

            addButtons.forEach(button => {
                button.addEventListener('click', async () => {
                    const link = button?.dataset?.link;
                    const card = button?.dataset?.card;
                    const board = button?.dataset?.board;

                    if (link && card && board) {
                        let data = new FormData();
                        data.append("card_id", card);
                        data.append("board", board);

                        await this.utilities.postDataToAPI(link, data, this.errorToastBody, this.errorToast, this.successToastBody, this.successToast);
                    }
                });
            });

            deleteButton.addEventListener('click', async () => {
                const link = deleteButton?.dataset?.link;
                const card = deleteButton?.dataset?.card;

                if (link && card) {
                    let data = new FormData();
                    data.append("card_id", card);

                    await this.utilities.postDataToAPI(link, data, this.errorToastBody, this.errorToast, this.successToastBody, this.successToast);
                }
            });
        });
    }

    setupQuantityModalEventListeners() {
        this.quantityModals.forEach(modal => {
            const inputField = modal.querySelector('.js-quantityInput');
            const submitButton = modal.querySelector('.js-quantityButton');
            const link = submitButton?.dataset?.link;

            if (link) {
                submitButton.addEventListener('click', async () => {
                    let data = new FormData();
                    data.append("quantity", inputField.value);
                    await this.utilities.postDataToAPI(link, data, this.errorToastBody, this.errorToast, this.successToastBody, this.successToast);
                });
            }
        });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new CardPage();
});
