/**
 * Google Analytics (gtag.js) — TrackForcePro Docs
 * ─────────────────────────────────────────────────
 * Update the MEASUREMENT_ID below to change the GA4
 * property across all docs pages in one place.
 */
(function () {
    var MEASUREMENT_ID = 'G-RP611E2183';

    // Load the gtag.js library
    var script = document.createElement('script');
    script.async = true;
    script.src = 'https://www.googletagmanager.com/gtag/js?id=' + MEASUREMENT_ID;
    document.head.appendChild(script);

    // Initialize dataLayer and gtag
    window.dataLayer = window.dataLayer || [];
    function gtag() {
        window.dataLayer.push(arguments);
    }
    gtag('js', new Date());
    gtag('config', MEASUREMENT_ID);
})();
