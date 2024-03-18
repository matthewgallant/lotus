/**
 * Script for Results Page
 */

class ResultsPage {
    constructor() {
        this.cardsEl = document.querySelector('.js-cards');
        this.cardEls = document.querySelectorAll('.js-card');
        this.page = 1;

        this.setupInfiniteScroll();
    }

    setupInfiniteScroll() {
        // Create intersection observer for last card
        this.observer = new IntersectionObserver(entries => {
            entries.forEach(async entry => {
                if (entry.isIntersecting) {
                    // Delete last observer when done
                    this.observer.unobserve(this.cardEls[this.cardEls.length - 1]);

                    // Increment the page state
                    this.page += 1;

                    // Request another page of cards
                    const page = `/search/results${window.location.search ? window.location.search + '&' : '?'}page=${this.page}`;
                    const res = await fetch(page);
                    if (res.status === 200) {
                        const data = await res.text();
                        if (data != null) {
                            // Inject cards HTML
                            this.cardsEl.innerHTML += data;

                            // Create observer for new last card
                            this.cardEls = document.querySelectorAll('.js-card');
                            if (this.cardEls.length % 12 == 0) {
                                this.observer.observe(this.cardEls[this.cardEls.length - 1]);
                            }
                        }
                    }
                }
            });
        });

        // Only observe if we have a full dataset
        if (this.cardEls.length % 12 == 0) {
            this.observer.observe(this.cardEls[this.cardEls.length - 1]);
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new ResultsPage();
});

