(function() {
  function fixFaviconForGithubPages() {
    if (!window.location.hostname.includes('github.io')) return;
    var repoName = window.location.pathname.split('/')[1] || 'sf-audit-extractor-docs';
    var basePath = '/' + repoName + '/icons/';
    var fav32 = document.getElementById('fav32');
    var fav16 = document.getElementById('fav16');
    var favshort = document.getElementById('favshort');
    if (fav32) fav32.href = basePath + 'Icon-32.png';
    if (fav16) fav16.href = basePath + 'Icon-16.png';
    if (favshort) favshort.href = basePath + 'Icon-32.png';
  }
  function markActiveNav() {
    var path = window.location.pathname.split('/').pop() || 'index.html';
    document.querySelectorAll('[data-nav]').forEach(function(link) {
      if (link.getAttribute('href') === path) {
        link.classList.add('active');
      }
    });
  }
  document.addEventListener('DOMContentLoaded', function() {
    fixFaviconForGithubPages();
    markActiveNav();
  });
})();
