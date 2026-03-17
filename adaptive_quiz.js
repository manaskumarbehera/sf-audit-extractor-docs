/**
 * TrackForcePro — Adaptive Quiz Client
 * ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 * Frontend adapter for the Python adaptive quiz API.
 * Falls back to local question bank when API is unavailable.
 *
 * Usage from quiz.html:
 *   AdaptiveQuiz.init(playerId)
 *   AdaptiveQuiz.getNextQuestion(mode).then(q => ...)
 *   AdaptiveQuiz.submitAnswer(questionId, selected, timeTaken).then(r => ...)
 *   AdaptiveQuiz.getProfile().then(p => ...)
 *   AdaptiveQuiz.getTopics().then(t => ...)
 */
(function () {
    'use strict';

    // ── Config ──
    var API_BASE = (function () {
        var origin = window.location.origin;
        // On GitHub Pages, no Python API — use fallback
        if (origin.indexOf('github.io') >= 0) return null;
        // Check if API port is specified
        if (origin.indexOf(':3000') >= 0) {
            // Node server — Python API is on port 8000
            return origin.replace(':3000', ':8000');
        }
        // Default: same origin with /api/quiz prefix
        return origin;
    })();

    var _playerId = null;
    var _apiAvailable = null; // null = unknown, true/false after probe
    var _profileCache = null;
    var _xpBarEl = null;

    // ── HTTP helper ──
    function apiCall(method, path, body) {
        if (!API_BASE) return Promise.reject('No API');

        return new Promise(function (resolve, reject) {
            var xhr = new XMLHttpRequest();
            xhr.open(method, API_BASE + path, true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.timeout = 5000;
            xhr.onload = function () {
                try {
                    var data = JSON.parse(xhr.responseText);
                    if (xhr.status >= 200 && xhr.status < 300) {
                        resolve(data);
                    } else {
                        reject(data);
                    }
                } catch (e) { reject(e); }
            };
            xhr.onerror = function () { reject('Network error'); };
            xhr.ontimeout = function () { reject('Timeout'); };
            xhr.send(body ? JSON.stringify(body) : null);
        });
    }

    // ── Probe API availability ──
    function probeApi() {
        if (!API_BASE) {
            _apiAvailable = false;
            return Promise.resolve(false);
        }
        return apiCall('GET', '/api/quiz/health')
            .then(function (data) {
                _apiAvailable = data && data.status === 'ok';
                if (_apiAvailable) {
                    console.log('[AdaptiveQuiz] API connected — ' + data.questions + ' questions, v' + data.version);
                }
                return _apiAvailable;
            })
            .catch(function () {
                _apiAvailable = false;
                console.log('[AdaptiveQuiz] API unavailable — using local questions');
                return false;
            });
    }

    // ── XP Bar UI ──
    function renderXpBar(container) {
        if (!_profileCache) return;
        var xp = _profileCache.total_xp || 0;
        var level = _profileCache.level || 1;
        var toNext = _profileCache.xp_to_next_level || 100;
        var currentLevelXp = xp - (xpForLevel(level) || 0);
        var levelRange = toNext + currentLevelXp;
        var pct = levelRange > 0 ? Math.min(100, Math.round((currentLevelXp / levelRange) * 100)) : 0;

        if (!_xpBarEl) {
            _xpBarEl = document.createElement('div');
            _xpBarEl.className = 'xp-bar-container';
            _xpBarEl.innerHTML =
                '<div class="xp-bar-label"></div>' +
                '<div class="xp-bar"><div class="xp-bar-fill"></div></div>' +
                '<div class="xp-level"></div>';
            container.insertBefore(_xpBarEl, container.firstChild);
        }

        _xpBarEl.querySelector('.xp-bar-label').textContent = 'Level ' + level + ' — ' + xp + ' XP';
        _xpBarEl.querySelector('.xp-bar-fill').style.width = pct + '%';
        _xpBarEl.querySelector('.xp-level').textContent = toNext + ' XP to Level ' + (level + 1);
    }

    function xpForLevel(level) {
        return Math.floor(100 * Math.pow(level, 1.5));
    }

    // ── Floating score popup ──
    function showFloatingScore(text, color) {
        var el = document.createElement('div');
        el.className = 'floating-score';
        el.textContent = text;
        if (color) el.style.color = color;
        document.body.appendChild(el);
        setTimeout(function () { el.remove(); }, 1100);
    }

    // ── Topic weakness chart (simple bar chart) ──
    function renderWeaknessChart(container, topicAccuracies) {
        if (!topicAccuracies) return;
        var html = '<div style="margin-top:20px;">';
        html += '<h4 style="font-size:14px;font-weight:700;margin-bottom:12px;color:var(--text);">Topic Mastery</h4>';

        var topics = Object.keys(topicAccuracies).sort(function (a, b) {
            return topicAccuracies[a] - topicAccuracies[b];
        });

        topics.forEach(function (topic) {
            var pct = topicAccuracies[topic] || 0;
            var barColor = pct >= 80 ? 'var(--success)' : pct >= 50 ? 'var(--warning)' : 'var(--danger)';
            html += '<div style="margin-bottom:8px;">';
            html += '<div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:2px;">';
            html += '<span style="color:var(--text-secondary);font-weight:500;">' + topic.replace(/_/g, ' ') + '</span>';
            html += '<span style="color:var(--text-muted);font-weight:600;">' + pct + '%</span>';
            html += '</div>';
            html += '<div style="height:6px;background:var(--border);border-radius:100px;overflow:hidden;">';
            html += '<div style="height:100%;width:' + pct + '%;background:' + barColor + ';border-radius:100px;transition:width 0.6s ease;"></div>';
            html += '</div></div>';
        });

        html += '</div>';
        container.innerHTML = html;
    }

    // ══════════════════════════════════════════
    //  PUBLIC API
    // ══════════════════════════════════════════
    window.AdaptiveQuiz = {
        /**
         * Initialize the adaptive quiz system.
         * @param {string} playerId - Player identifier (email)
         * @returns {Promise<boolean>} - Whether the API is available
         */
        init: function (playerId) {
            _playerId = playerId;
            return probeApi().then(function (available) {
                if (available && playerId) {
                    return apiCall('GET', '/api/quiz/profile/' + encodeURIComponent(playerId))
                        .then(function (profile) {
                            _profileCache = profile;
                            return true;
                        })
                        .catch(function () { return false; });
                }
                return false;
            });
        },

        /** Whether the adaptive API is connected */
        isAvailable: function () {
            return _apiAvailable === true;
        },

        /**
         * Get the next adaptive question.
         * @param {string} [mode] - Game mode filter
         * @param {string} [topic] - Topic filter
         * @returns {Promise<Object>} - Question object
         */
        getNextQuestion: function (mode, topic) {
            if (!_apiAvailable || !_playerId) return Promise.reject('Not available');
            var params = '?player_id=' + encodeURIComponent(_playerId);
            if (mode) params += '&mode=' + encodeURIComponent(mode);
            if (topic) params += '&topic=' + encodeURIComponent(topic);
            return apiCall('GET', '/api/quiz/next' + params);
        },

        /**
         * Submit an answer and get feedback + XP.
         * @param {string} questionId
         * @param {number} selectedIndex
         * @param {number} timeTaken - Seconds
         * @returns {Promise<Object>} - Answer result with XP, streak, etc.
         */
        submitAnswer: function (questionId, selectedIndex, timeTaken) {
            if (!_apiAvailable || !_playerId) return Promise.reject('Not available');
            return apiCall('POST', '/api/quiz/answer', {
                player_id: _playerId,
                question_id: questionId,
                selected: selectedIndex,
                time_taken: timeTaken || 0,
            }).then(function (result) {
                // Update cached profile
                if (_profileCache) {
                    _profileCache.total_xp = result.total_xp;
                    _profileCache.level = result.level;
                    _profileCache.xp_to_next_level = xpForLevel(result.level + 1) - result.total_xp;
                    _profileCache.current_streak = result.streak;
                    _profileCache.accuracy_pct = result.accuracy_pct;
                }

                // Show floating score if correct
                if (result.correct && result.xp_earned > 0) {
                    showFloatingScore('+' + result.xp_earned + ' XP', 'var(--success)');
                }

                // Show level up
                if (result.level_up) {
                    setTimeout(function () {
                        showFloatingScore('LEVEL ' + result.level + '!', 'var(--primary)');
                    }, 500);
                }

                return result;
            });
        },

        /**
         * Get the player's profile with topic accuracies.
         * @returns {Promise<Object>}
         */
        getProfile: function () {
            if (!_apiAvailable || !_playerId) return Promise.reject('Not available');
            return apiCall('GET', '/api/quiz/profile/' + encodeURIComponent(_playerId))
                .then(function (profile) {
                    _profileCache = profile;
                    return profile;
                });
        },

        /**
         * Get topics list with player accuracy.
         * @returns {Promise<Object>}
         */
        getTopics: function () {
            if (!_apiAvailable || !_playerId) return Promise.reject('Not available');
            return apiCall('GET', '/api/quiz/topics?player_id=' + encodeURIComponent(_playerId));
        },

        /**
         * Render the XP bar into a container element.
         * @param {HTMLElement} container
         */
        renderXpBar: function (container) {
            if (_profileCache && container) {
                renderXpBar(container);
            }
        },

        /**
         * Render weakness chart into a container.
         * @param {HTMLElement} container
         */
        renderWeaknessChart: function (container) {
            if (_profileCache && container) {
                renderWeaknessChart(container, _profileCache.topic_accuracies);
            }
        },

        /** Get cached profile data */
        getCachedProfile: function () { return _profileCache; },

        /** Reset a player's adaptive state */
        reset: function () {
            if (!_apiAvailable || !_playerId) return Promise.reject('Not available');
            return apiCall('POST', '/api/quiz/reset/' + encodeURIComponent(_playerId));
        },
    };
})();
