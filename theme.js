/* ═══════════════════════════════════════════════════
   TrackForcePro — Shared Theme Toggle + Utilities
   ═══════════════════════════════════════════════════ */
(function() {
    'use strict';

    /* ── Apply saved theme instantly (call in <head> to prevent flash) ── */
    var saved = localStorage.getItem('tfp_theme');
    if (saved === 'dark' || (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
        document.documentElement.setAttribute('data-theme', 'dark');
    }

    /* ── GitHub Pages icon fix ── */
    if (window.location.hostname.includes('github.io')) {
        var repoName = window.location.pathname.split('/')[1] || 'sf-audit-extractor-docs';
        var basePath = '/' + repoName + '/icons/';
        var fav32 = document.getElementById('fav32');
        var fav16 = document.getElementById('fav16');
        var favshort = document.getElementById('favshort');
        if (fav32) fav32.href = basePath + 'Icon-32.png';
        if (fav16) fav16.href = basePath + 'Icon-16.png';
        if (favshort) favshort.href = basePath + 'Icon-32.png';
    }

    /* ── Theme Toggle ── */
    window.toggleTheme = function() {
        var html = document.documentElement;
        var current = html.getAttribute('data-theme');
        var next = current === 'dark' ? 'light' : 'dark';
        if (next === 'light') {
            html.removeAttribute('data-theme');
        } else {
            html.setAttribute('data-theme', 'dark');
        }
        localStorage.setItem('tfp_theme', next);
        updateThemeToggle();
    };

    function updateThemeToggle() {
        var isDark = document.documentElement.getAttribute('data-theme') === 'dark';
        var btns = document.querySelectorAll('.theme-toggle');
        btns.forEach(function(btn) {
            var icon = btn.querySelector('.theme-icon');
            var label = btn.querySelector('.theme-label');
            if (icon) icon.textContent = isDark ? '☀️' : '🌙';
            if (label) label.textContent = isDark ? 'Light' : 'Dark';
        });
    }

    /* ── GitHub Pages logo fix (after DOM) ── */
    function fixGitHubLogos() {
        if (!window.location.hostname.includes('github.io')) return;
        var repoName = window.location.pathname.split('/')[1] || 'sf-audit-extractor-docs';
        var basePath = '/' + repoName + '/icons/';
        var logo = document.getElementById('header-logo');
        if (logo) logo.src = basePath + 'Icon-128.png';
    }

    /* ── Scroll Reveal Animation ── */
    function initScrollReveal() {
        var els = document.querySelectorAll('.reveal');
        if (!els.length) return;
        var obs = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    obs.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });
        els.forEach(function(el) { obs.observe(el); });
    }

    /* ── Init ── */
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            updateThemeToggle();
            fixGitHubLogos();
            initScrollReveal();
        });
    } else {
        updateThemeToggle();
        fixGitHubLogos();
        initScrollReveal();
    }
})();
