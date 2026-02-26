/**
 * ui-config.js — Dynamic UI Content Loader
 * Fetches all UIAssets from /api/ui-config and applies them to
 * elements tagged with data-ui-key="key" attributes.
 * Falls back gracefully if API is unavailable.
 */
(function () {
    'use strict';

    const CACHE_KEY = 'em_ui_config';
    const CACHE_TTL = 60 * 1000; // 1 minute

    async function loadUIConfig() {
        // Try sessionStorage cache first
        try {
            const cached = sessionStorage.getItem(CACHE_KEY);
            if (cached) {
                const { ts, data } = JSON.parse(cached);
                if (Date.now() - ts < CACHE_TTL) {
                    applyConfig(data);
                    return;
                }
            }
        } catch (e) { /* ignore */ }

        try {
            const res = await fetch('/api/ui-config');
            if (!res.ok) return;
            const config = await res.json();

            // Cache it
            try {
                sessionStorage.setItem(CACHE_KEY, JSON.stringify({
                    ts: Date.now(),
                    data: config,
                }));
            } catch (e) { /* ignore quota errors */ }

            applyConfig(config);
        } catch (e) {
            // API unavailable — degrade gracefully, keep hardcoded text
            console.warn('[UI Config] Could not load dynamic config:', e.message);
        }
    }

    function applyConfig(config) {
        document.querySelectorAll('[data-ui-key]').forEach(el => {
            const key = el.dataset.uiKey;
            const value = config[key];
            if (value === undefined || value === null) return;

            if (el.tagName === 'IMG') {
                el.src = value;
                el.setAttribute('loading', 'lazy');
            } else if (el.tagName === 'INPUT' && el.type !== 'submit') {
                el.placeholder = value;
            } else if (el.dataset.uiTarget === 'html') {
                el.innerHTML = value;
            } else {
                el.textContent = value;
            }
        });

        // Fire custom event so other scripts can react to config load
        document.dispatchEvent(new CustomEvent('uiConfigLoaded', { detail: config }));

        // Store config globally for admin panel access
        window.__uiConfig = config;
    }

    // Expose for manual refresh
    window.refreshUIConfig = function () {
        sessionStorage.removeItem(CACHE_KEY);
        loadUIConfig();
    };

    // Load on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', loadUIConfig);
    } else {
        loadUIConfig();
    }
})();
