class WindComponent {
    /**
     * @param {string} containerId The ID of the DOM element to render the component in.
     */
    constructor(containerId, title = 'Wind') {
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
            <div class="wind-widget">
            <h3 class="widget-title">${this.title}</h3>
                <div class="wind-main">
                    <div class="row">
                        <div class="wind-speed">
                            <span class="speed-value">--</span>
                            <span class="speed-unit">knots</span>
                        </div>
                         <div class="beaufort-info">
                            <span class="beaufort-value">--</span>
                            <span><div class="beaufort-title">Beaufort</div> <div class="beaufort-name">---</div></span>
                     </div>
                    </div>
                    <div class="wind-direction">
                        <div class="direction-arrow-container">
                            <svg class="direction-arrow" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                                <path d="M12 2L6.152 22 12 17.5 17.848 22 12 2z"/>
                            </svg>
                        </div>
                        <div class="direction-info">
                            <span class="direction-degrees">---°</span>
                            <span class="direction-cardinal">---</span>
                        </div>
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
        this.speedValueEl = this.container.querySelector('.speed-value');
        this.directionArrowEl = this.container.querySelector('.direction-arrow');
        this.directionDegreesEl = this.container.querySelector('.direction-degrees');
        this.directionCardinalEl = this.container.querySelector('.direction-cardinal');
        this.beaufortValueEl = this.container.querySelector('.beaufort-value');
        this.beaufortNameEl = this.container.querySelector('.beaufort-name');
    }

    /**
     * Converts wind speed in knots to the Beaufort scale number.
     * @param {number} knots Wind speed in knots.
     * @returns {number} The corresponding Beaufort force number.
     * @private
     */
    _knotsToBeaufort(knots) {
        if (knots < 1) return 0;
        if (knots <= 3) return 1;
        if (knots <= 6) return 2;
        if (knots <= 10) return 3;
        if (knots <= 16) return 4;
        if (knots <= 21) return 5;
        if (knots <= 27) return 6;
        if (knots <= 33) return 7;
        if (knots <= 40) return 8;
        if (knots <= 47) return 9;
        if (knots <= 55) return 10;
        if (knots <= 63) return 11;
        return 12;
    }

    _beaufortNameFromKnots(k) {
          const scale = [{
            max: 1,
            label: 'Calm'
          }, {
            max: 3,
            label: 'Light Air'
          }, {
            max: 6,
            label: 'Light Breeze'
          }, {
            max: 10,
            label: 'Gentle Breeze'
          }, {
            max: 16,
            label: 'Moderate Breeze'
          }, {
            max: 21,
            label: 'Fresh Breeze'
          }, {
            max: 27,
            label: 'Strong Breeze'
          }, {
            max: 33,
            label: 'Near Gale'
          }, {
            max: 40,
            label: 'Gale'
          }, {
            max: 47,
            label: 'Strong Gale'
          }, {
            max: 55,
            label: 'Storm'
          }, {
            max: 63,
            label: 'Violent Storm'
          }, {
            max: Infinity,
            label: 'Hurricane'
          }, ];
          for (let i = 0; i < scale.length; i++) {
            if (k <= scale[i].max) return scale[i].label;
          }
          return 'Hurricane';
    }

    /**
     * Converts degrees to a cardinal direction.
     * @param {number} deg The direction in degrees.
     * @returns {string} The cardinal direction (e.g., N, NE, S).
     * @private
     */
    _degreesToCardinal(deg) {
        const directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW', 'N'];
        const index = Math.round((deg % 360) / 45);
        return directions[index];
    }

    /**
     * Updates the component with new wind data.
     * @param {number} speed Wind speed in knots.
     * @param {number} direction Wind direction in degrees (0-360).
     */
    update(speed, direction) {
        if (speed === null || direction === null) return;

        // Update speed
        this.speedValueEl.textContent = speed.toFixed(1);

        // Update direction arrow (smooth rotation via CSS transition)
        this.directionArrowEl.style.transform = `rotate(${direction}deg)`;

        // Update direction text
        this.directionDegreesEl.textContent = `${Math.round(direction)}°`;
        this.directionCardinalEl.textContent = this._degreesToCardinal(direction);
        this.beaufortValueEl.textContent = this._knotsToBeaufort(speed);
        this.beaufortNameEl.textContent = this._beaufortNameFromKnots(speed);
    }
}