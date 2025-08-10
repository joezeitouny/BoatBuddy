class NavigationComponent {
    /**
     * @param {string} containerId The ID of the DOM element to render the component in.
     * @param {string} [title='Navigation'] The title to display on the widget.
     */
    constructor(containerId, title = 'Navigation') {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            console.error(`Container with ID "${containerId}" not found.`);
            return;
        }
        this.title = title;
        this._createHTML();
        this._queryElements();
    }

    /**
     * Creates and injects the component's HTML structure.
     * @private
     */
    _createHTML() {
        this.container.innerHTML = `
            <div class="nav-widget">
                <h3 class="widget-title">${this.title}</h3>
                <div class="nav-heading">
                    <div class="compass-container">
                        <svg class="compass-rose" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
                            <!-- Compass Rose background -->
                            <circle cx="50" cy="50" r="48" fill="#fff" stroke="#e9ecef" stroke-width="2"/>
                            <path d="M50 10 L55 20 L50 25 L45 20 Z" fill="#e74c3c"/> <!-- North -->
                            <text x="50" y="8" font-size="8" text-anchor="middle" fill="#333">N</text>
                            <text x="50" y="96" font-size="8" text-anchor="middle" fill="#333">S</text>
                            <text x="94" y="53" font-size="8" text-anchor="middle" fill="#333">E</text>
                            <text x="6" y="53" font-size="8" text-anchor="middle" fill="#333">W</text>
                             <!-- Needle/Pointer -->
                            <path class="compass-needle" d="M50 2 L46 12 L50 98 L54 12 Z" fill="#007bff" />
                        </svg>
                    </div>
                    <span class="heading-value">---°</span>
                </div>
                <div class="nav-speeds">
                    <div class="speed-item">
                        <span class="speed-value" id="sog-value">--</span>
                        <span class="speed-label">SOG (knots)</span>
                    </div>
                    <div class="speed-item">
                        <span class="speed-value" id="sow-value">--</span>
                        <span class="speed-label">SOW (knots)</span>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Selects the dynamic elements from the created HTML.
     * @private
     */
    _queryElements() {
        this.compassNeedleEl = this.container.querySelector('.compass-needle');
        this.headingValueEl = this.container.querySelector('.heading-value');
        this.sogValueEl = this.container.querySelector('#sog-value');
        this.sowValueEl = this.container.querySelector('#sow-value');
    }

    /**
     * Updates the component with new navigation data.
     * @param {number} heading Compass heading in degrees (0-360).
     * @param {number} sog Speed Over Ground in knots.
     * @param {number} sow Speed Over Water in knots.
     */
    update(heading, sog, sow) {
        if (heading === null || sog === null || sow === null) return;

        // Update heading display
        this.compassNeedleEl.style.transformOrigin = '50px 50px'; // Set rotation origin to center of the SVG
        this.compassNeedleEl.style.transform = `rotate(${heading}deg)`;
        this.headingValueEl.textContent = `${Math.round(heading)}°`;

        // Update speeds
        this.sogValueEl.textContent = sog.toFixed(1);
        this.sowValueEl.textContent = sow.toFixed(1);
    }
}
