/**
 * Script for Deck Page
 */

class DeckPage {
    constructor() {
        this.totalPrice = 0;
        this.priceBadgeEl = document.querySelector('.js-priceBadge');
        this.mainboardRows = document.querySelectorAll('#mainboard-tab-pane [data-scryfall-id]');
        this.sideboardRows = document.querySelectorAll('#sideboard-tab-pane [data-scryfall-id]');
        this.gatherRows = document.querySelectorAll('#gather-tab-pane [data-scryfall-id]');
        this.mainboardCardImageEl = document.querySelector('#mainboardCardImage');
        this.sideboardCardImageEl = document.querySelector('#sideboardCardImage');
        this.gatherCardImageEl = document.querySelector('#gatherCardImage');
        this.successToast = bootstrap.Toast.getOrCreateInstance(document.querySelector('#successToast'));
        this.successToastBody = document.querySelector('#successToast .js-toastBody');
        this.errorToast = bootstrap.Toast.getOrCreateInstance(document.querySelector('#errorToast'));
        this.errorToastBody = document.querySelector('#errorToast .js-toastBody');

        this.utilities = new Utilities();

        this.utilities.enableDynamicCardImages(this.mainboardRows, this.mainboardCardImageEl);
        this.utilities.enableDynamicCardImages(this.sideboardRows, this.sideboardCardImageEl);
        this.utilities.enableDynamicCardImages(this.gatherRows, this.gatherCardImageEl);
        this.setupMainboardRowActionEventListeners();
        this.setupSideboardRowActionEventListeners();
    }

    setupMainboardRowActionEventListeners() {
        this.mainboardRows.forEach(row => {
            this.setupRowActionEventListeners(row);
        });
    }

    setupSideboardRowActionEventListeners() {
        this.sideboardRows.forEach(row => {
            this.setupRowActionEventListeners(row);
        });
    }

    setupRowActionEventListeners(row) {
        this.setupMoveBoardEventListsner(row);
        this.setupSetCommanderEventListsner(row);
        this.setupDeleteEventListsner(row);
    }

    setupMoveBoardEventListsner(row) {
        const moveBoardButton = row.querySelector(".js-moveBoardButton");
        moveBoardButton.addEventListener('click', async () => {
            const link = moveBoardButton?.dataset?.link;
            const assoc = moveBoardButton?.dataset?.assoc;
            const board = moveBoardButton?.dataset?.board;

            if (link && assoc && board) {
                let data = new FormData();
                data.append("assoc_id", assoc);
                data.append("board", board);

                const status = await this.utilities.postDataToAPI(link, data, this.errorToastBody, this.errorToast, this.successToastBody, this.successToast);
                if (status) {
                    row.parentNode.removeChild(row);
                }
            }
        });
    }

    setupSetCommanderEventListsner(row) {
        const setCommanderButton = row.querySelector(".js-setCommanderButton");
        setCommanderButton.addEventListener('click', async () => {
            const link = setCommanderButton?.dataset?.link;
            const assoc = setCommanderButton?.dataset?.assoc;
            const type = setCommanderButton?.dataset?.type;

            if (link && assoc && type) {
                let data = new FormData();
                data.append("assoc_id", assoc);
                data.append("set_commander", type);

                await await this.utilities.postDataToAPI(link, data, this.errorToastBody, this.errorToast, this.successToastBody, this.successToast);
            }
        });
    }

    setupDeleteEventListsner(row) {
        const deleteButton = row.querySelector(".js-deleteButton");
        deleteButton.addEventListener('click', async () => {
            const link = deleteButton?.dataset?.link;
            const assoc = deleteButton?.dataset?.assoc;

            if (link && assoc) {
                let data = new FormData();
                data.append("assoc_id", assoc);

                const status = await this.utilities.postDataToAPI(link, data, this.errorToastBody, this.errorToast, this.successToastBody, this.successToast);
                if (status) {
                    row.parentNode.removeChild(row);
                }
            }
        });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new DeckPage();
});
