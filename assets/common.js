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

  function initRevealOnScroll() {
    var items = document.querySelectorAll('.reveal');
    if (!items.length || !('IntersectionObserver' in window)) {
      items.forEach(function(el) { el.classList.add('show'); });
      return;
    }
    var obs = new IntersectionObserver(function(entries) {
      entries.forEach(function(entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('show');
          obs.unobserve(entry.target);
        }
      });
    }, { threshold: 0.2 });
    items.forEach(function(el) { obs.observe(el); });
  }

  function extractPlaylistId(url) {
    if (!url) return '';
    var match = String(url).match(/[?&]list=([A-Za-z0-9_-]+)/);
    return match ? match[1] : '';
  }

  function initYoutubeEmbedToggle() {
    var input = document.getElementById('ytPlaylistInput');
    var btn = document.getElementById('ytToggleBtn');
    var clearBtn = document.getElementById('ytClearBtn');
    var frameWrap = document.getElementById('ytEmbedWrap');
    var frame = document.getElementById('ytEmbedFrame');
    var hint = document.getElementById('ytEmbedHint');
    if (!input || !btn || !frameWrap || !frame || !hint) return;

    btn.addEventListener('click', function() {
      var raw = input.value.trim();
      var playlistId = extractPlaylistId(raw) || raw;
      if (!playlistId) {
        hint.textContent = 'Paste a playlist URL or playlist ID first.';
        return;
      }
      frame.src = 'https://www.youtube.com/embed/videoseries?list=' + encodeURIComponent(playlistId);
      frameWrap.classList.remove('hidden');
      hint.textContent = 'Playlist embed enabled. You can hide it anytime.';
    });

    if (clearBtn) {
      clearBtn.addEventListener('click', function() {
        frame.src = '';
        frameWrap.classList.add('hidden');
        hint.textContent = 'Embed hidden. Paste playlist URL anytime.';
      });
    }
  }

  document.addEventListener('DOMContentLoaded', function() {
    fixFaviconForGithubPages();
    markActiveNav();
    initRevealOnScroll();
    initYoutubeEmbedToggle();
  });
})();
