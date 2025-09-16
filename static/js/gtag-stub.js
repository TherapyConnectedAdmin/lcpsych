/* Local stub for gtag/dataLayer to avoid network calls */
window.dataLayer = window.dataLayer || [];
function gtag(){ dataLayer.push(arguments); }
// Initialize with a local config id
gtag('js', new Date());
gtag('config', 'LOCAL-STUB');
