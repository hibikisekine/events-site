// グローバル変数
let currentEvents = [];
let currentWeather = null;

// ページ読み込み時の初期化
document.addEventListener('DOMContentLoaded', function() {
    loadData();
    setupEventListeners();
});

// イベントリスナーの設定
function setupEventListeners() {
    // フィルター変更時のイベント
    document.getElementById('category-filter').addEventListener('change', filterEvents);
    document.getElementById('city-filter').addEventListener('change', filterEvents);
    document.getElementById('location-filter').addEventListener('change', filterEvents);
    document.getElementById('free-filter').addEventListener('change', filterEvents);
    document.getElementById('child-friendly-filter').addEventListener('change', filterEvents);
    document.getElementById('parking-filter').addEventListener('change', filterEvents);
}

// データの読み込み
async function loadData() {
    try {
        showLoading();
        
        // イベントと天気情報を同時に取得
        const response = await fetch('/api/events');
        const data = await response.json();
        
        if (response.ok) {
            currentEvents = data.events || [];
            currentWeather = data.weather;
            
            updateWeatherDisplay();
            updateEventsDisplay();
        } else {
            showError('データの取得に失敗しました: ' + data.error);
        }
    } catch (error) {
        showError('ネットワークエラーが発生しました: ' + error.message);
    }
}

// 天気表示の更新
function updateWeatherDisplay() {
    if (!currentWeather) {
        // 天気データがない場合のフォールバック
        const weatherInfo = document.getElementById('weather-info');
        const weatherIcon = document.getElementById('weather-icon');
        
        weatherInfo.innerHTML = `
            <div class="weather-details">
                <div class="weather-main">天気情報を取得中...</div>
                <div class="weather-temp">--°C</div>
                <div class="weather-humidity">湿度: --%</div>
                <div class="weather-rain">降水確率: --%</div>
            </div>
        `;
        
        weatherIcon.innerHTML = '<i class="fas fa-sun fa-3x text-warning"></i>';
        return;
    }
    
    const weatherInfo = document.getElementById('weather-info');
    const weatherIcon = document.getElementById('weather-icon');
    
    // 今日の天気を取得
    const today = new Date().toISOString().split('T')[0];
    const todayWeather = currentWeather.forecast ? currentWeather.forecast.find(f => f.date === today) : null;
    
    if (todayWeather) {
        weatherInfo.innerHTML = `
            <div class="weather-details">
                <div class="weather-main">${todayWeather.description || todayWeather.condition || '晴れ'}</div>
                <div class="weather-temp">${todayWeather.temperature || todayWeather.temp_max || '--'}°C</div>
                <div class="weather-humidity">湿度: ${todayWeather.humidity || '--'}%</div>
                <div class="weather-rain">降水確率: ${Math.round(todayWeather.rain_probability || todayWeather.precipitation || 0)}%</div>
            </div>
        `;
        
        // 天気アイコンの更新
        updateWeatherIcon(weatherIcon, todayWeather);
    } else {
        // 今日の天気データがない場合のフォールバック
        weatherInfo.innerHTML = `
            <div class="weather-details">
                <div class="weather-main">天気情報を取得中...</div>
                <div class="weather-temp">--°C</div>
                <div class="weather-humidity">湿度: --%</div>
                <div class="weather-rain">降水確率: --%</div>
            </div>
        `;
        
        weatherIcon.innerHTML = '<i class="fas fa-sun fa-3x text-warning"></i>';
    }
}

// 天気アイコンの更新
function updateWeatherIcon(iconElement, weather) {
    let iconClass = 'fas fa-sun';
    let iconColor = 'text-warning';
    
    if (weather.is_rainy) {
        iconClass = 'fas fa-cloud-rain';
        iconColor = 'text-info';
    } else if (weather.main === 'Clouds') {
        iconClass = 'fas fa-cloud';
        iconColor = 'text-secondary';
    } else if (weather.main === 'Snow') {
        iconClass = 'fas fa-snowflake';
        iconColor = 'text-info';
    }
    
    iconElement.innerHTML = `<i class="${iconClass} fa-3x ${iconColor}"></i>`;
}

// イベント表示の更新
function updateEventsDisplay() {
    const container = document.getElementById('events-container');
    const countElement = document.getElementById('event-count');
    
    if (currentEvents.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-calendar-times"></i>
                <h5>イベントが見つかりません</h5>
                <p>現在、おすすめのイベントはありません。</p>
                <button class="btn btn-primary" onclick="scrapeEvents()">
                    <i class="fas fa-download me-1"></i>
                    イベント情報を更新
                </button>
            </div>
        `;
        countElement.textContent = '0件';
        return;
    }
    
    // イベントカードの生成
    const eventCards = currentEvents.map(event => createEventCard(event)).join('');
    container.innerHTML = eventCards;
    countElement.textContent = `${currentEvents.length}件`;
}

// イベントカードの作成
function createEventCard(event) {
    const tags = generateEventTags(event);
    const score = Math.round(event.suitability_score * 100);
    
    return `
        <div class="card event-card" onclick="showEventDetails('${event.id}')">
            <div class="card-body position-relative">
                <div class="suitability-score">適合度: ${score}%</div>
                
                <h5 class="event-title">${escapeHtml(event.title)}</h5>
                
                <div class="event-date">
                    <i class="fas fa-calendar me-1"></i>
                    ${formatDate(event.date)} ${event.time ? `(${event.time})` : ''}
                </div>
                
                <div class="event-location">
                    <i class="fas fa-map-marker-alt me-1"></i>
                    ${escapeHtml(event.location || '場所未定')}
                    ${event.location && event.location.includes('市') ? `<span class="badge bg-info ms-2">${event.location.match(/[^市]*市/)?.[0] || ''}</span>` : ''}
                </div>
                
                ${event.description ? `
                    <div class="event-description">
                        ${escapeHtml((event.description || '').substring(0, 150))}${(event.description || '').length > 150 ? '...' : ''}
                    </div>
                ` : ''}
                
                <div class="event-tags">
                    ${tags}
                </div>
                
                ${event.recommendation_reason ? `
                    <div class="recommendation-reason">
                        <i class="fas fa-lightbulb text-warning me-1"></i>
                        <small class="text-muted">${escapeHtml(event.recommendation_reason)}</small>
                    </div>
                ` : ''}
            </div>
        </div>
    `;
}

// イベントタグの生成
function generateEventTags(event) {
    const tags = [];
    
    if (event.is_indoor) {
        tags.push('<span class="event-tag tag-indoor">屋内</span>');
    } else {
        tags.push('<span class="event-tag tag-outdoor">屋外</span>');
    }
    
    if (event.is_free) {
        tags.push('<span class="event-tag tag-free">無料</span>');
    }
    
    if (event.child_friendly) {
        tags.push('<span class="event-tag tag-child-friendly">子連れOK</span>');
    }
    
    if (event.has_parking) {
        tags.push('<span class="event-tag tag-parking">駐車場</span>');
    }
    
    if (event.weather_dependent) {
        tags.push('<span class="event-tag tag-weather-dependent">天候依存</span>');
    }
    
    if (event.rain_cancellation) {
        tags.push(`<span class="event-tag tag-weather-dependent">${event.rain_cancellation}</span>`);
    }
    
    return tags.join('');
}

// イベント詳細の表示
function showEventDetails(eventId) {
    const event = currentEvents.find(e => e.id == eventId);
    if (!event) return;
    
    const modal = new bootstrap.Modal(document.getElementById('eventModal'));
    const titleElement = document.getElementById('eventModalTitle');
    const bodyElement = document.getElementById('eventModalBody');
    const linkElement = document.getElementById('eventModalLink');
    
    titleElement.textContent = event.title;
    
    bodyElement.innerHTML = `
        <div class="row">
            <div class="col-md-6">
                <h6><i class="fas fa-calendar me-2"></i>日時</h6>
                <p>${formatDate(event.date)} ${event.time || ''}</p>
                
                <h6><i class="fas fa-map-marker-alt me-2"></i>場所</h6>
                <p>${escapeHtml(event.location || '場所未定')}</p>
                
                <h6><i class="fas fa-tag me-2"></i>カテゴリ</h6>
                <p>${escapeHtml(event.category || 'カテゴリ未定')}</p>
            </div>
            <div class="col-md-6">
                <h6><i class="fas fa-info-circle me-2"></i>詳細</h6>
                <p>${escapeHtml(event.description || '詳細情報はありません')}</p>
                
                <h6><i class="fas fa-star me-2"></i>特徴</h6>
                <ul class="list-unstyled">
                    ${event.is_indoor ? '<li><i class="fas fa-home text-primary me-1"></i>屋内イベント</li>' : '<li><i class="fas fa-tree text-success me-1"></i>屋外イベント</li>'}
                    ${event.is_free ? '<li><i class="fas fa-gift text-danger me-1"></i>無料</li>' : '<li><i class="fas fa-yen-sign text-warning me-1"></i>有料</li>'}
                    ${event.child_friendly ? '<li><i class="fas fa-baby text-warning me-1"></i>子連れOK</li>' : ''}
                    ${event.has_parking ? '<li><i class="fas fa-car text-info me-1"></i>駐車場あり</li>' : ''}
                </ul>
            </div>
        </div>
        
        ${event.weather_info ? `
            <div class="mt-3">
                <h6><i class="fas fa-cloud-sun me-2"></i>当日の天気予報</h6>
                <p>${event.weather_info.description}、${event.weather_info.temperature}°C</p>
            </div>
        ` : ''}
    `;
    
    if (event.source_url) {
        linkElement.href = event.source_url;
        linkElement.style.display = 'inline-block';
    } else {
        linkElement.style.display = 'none';
    }
    
    modal.show();
}

// フィルター機能
function filterEvents() {
    // フィルター適用中の表示
    showFilterLoading();
    
    const category = document.getElementById('category-filter').value;
    const city = document.getElementById('city-filter').value;
    const location = document.getElementById('location-filter').value;
    const freeOnly = document.getElementById('free-filter').checked;
    const childFriendly = document.getElementById('child-friendly-filter').checked;
    const parkingRequired = document.getElementById('parking-filter').checked;
    
    // フィルターパラメータの構築
    const params = new URLSearchParams();
    if (category) params.append('category', category);
    if (city) params.append('city', city);
    if (location) params.append(location === 'indoor' ? 'indoor_only' : 'outdoor_only', 'true');
    if (freeOnly) params.append('free_only', 'true');
    if (childFriendly) params.append('child_friendly', 'true');
    if (parkingRequired) params.append('parking_required', 'true');
    
    // APIからフィルター結果を取得
    fetch(`/api/filter?${params.toString()}`)
        .then(response => {
            console.log('フィルターレスポンス:', response.status, response.statusText);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('フィルター結果:', data);
            console.log('eventsプロパティの存在:', !!data.events);
            console.log('eventsの型:', typeof data.events);
            console.log('eventsの長さ:', data.events ? data.events.length : 'undefined');
            
            if (data && data.events) {
                console.log('✅ 正常なレスポンス - イベントを更新');
                currentEvents = data.events.map(event => ({
                    ...event,
                    suitability_score: event.suitability_score || 0.5 // デフォルトスコア
                }));
                updateEventsDisplay();
                
                // フィルター適用完了の通知
                showFilterSuccess();
            } else {
                console.warn('⚠️ フィルター結果にeventsプロパティがありません:', data);
                currentEvents = [];
                updateEventsDisplay();
                showFilterSuccess();
            }
        })
        .catch(error => {
            console.error('❌ フィルターエラー:', error);
            showFilterError();
            
            // エラー時は全イベントを表示
            loadData();
        });
}

// データの更新
function refreshData() {
    loadData();
}

// イベント情報のスクレイピング
async function scrapeEvents() {
    try {
        showLoading();
        
        const response = await fetch('/api/scrape-events');
        const data = await response.json();
        
        if (response.ok) {
            showSuccess(data.message);
            loadData(); // 新しいデータを読み込み
        } else {
            showError('スクレイピングに失敗しました: ' + data.error);
        }
    } catch (error) {
        showError('スクレイピングエラー: ' + error.message);
    }
}

// ローディング表示
function showLoading() {
    const container = document.getElementById('events-container');
    container.innerHTML = `
        <div class="loading-spinner">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">読み込み中...</span>
            </div>
            <p class="mt-2">データを読み込み中...</p>
        </div>
    `;
}

// エラー表示
function showError(message) {
    const container = document.getElementById('events-container');
    container.innerHTML = `
        <div class="error-message">
            <i class="fas fa-exclamation-triangle me-2"></i>
            ${escapeHtml(message)}
        </div>
    `;
}

// 成功メッセージ表示
function showSuccess(message) {
    const container = document.getElementById('events-container');
    const successDiv = document.createElement('div');
    successDiv.className = 'success-message';
    successDiv.innerHTML = `
        <i class="fas fa-check-circle me-2"></i>
        ${escapeHtml(message)}
    `;
    container.insertBefore(successDiv, container.firstChild);
    
    // 3秒後にメッセージを削除
    setTimeout(() => {
        if (successDiv.parentNode) {
            successDiv.parentNode.removeChild(successDiv);
        }
    }, 3000);
}

// フィルター適用中の表示
function showFilterLoading() {
    const filterSection = document.querySelector('.filter-section');
    const loadingDiv = document.createElement('div');
    loadingDiv.id = 'filter-loading';
    loadingDiv.className = 'filter-loading';
    loadingDiv.innerHTML = `
        <div class="spinner-border spinner-border-sm text-primary me-2" role="status">
            <span class="visually-hidden">フィルター適用中...</span>
        </div>
        <span>フィルター適用中...</span>
    `;
    
    // 既存のローディング表示を削除
    const existingLoading = document.getElementById('filter-loading');
    if (existingLoading) {
        existingLoading.remove();
    }
    
    filterSection.appendChild(loadingDiv);
}

// フィルター適用完了の表示
function showFilterSuccess() {
    const loadingDiv = document.getElementById('filter-loading');
    if (loadingDiv) {
        loadingDiv.innerHTML = `
            <i class="fas fa-check-circle text-success me-2"></i>
            <span>フィルター適用完了</span>
        `;
        loadingDiv.className = 'filter-success';
        
        // 2秒後に削除
        setTimeout(() => {
            if (loadingDiv.parentNode) {
                loadingDiv.parentNode.removeChild(loadingDiv);
            }
        }, 2000);
    }
}

// フィルターエラーの表示
function showFilterError() {
    const loadingDiv = document.getElementById('filter-loading');
    if (loadingDiv) {
        loadingDiv.innerHTML = `
            <i class="fas fa-exclamation-triangle text-danger me-2"></i>
            <span>フィルター適用エラー</span>
        `;
        loadingDiv.className = 'filter-error';
        
        // 3秒後に削除
        setTimeout(() => {
            if (loadingDiv.parentNode) {
                loadingDiv.parentNode.removeChild(loadingDiv);
            }
        }, 3000);
    }
}

// ユーティリティ関数
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(dateString) {
    const date = new Date(dateString);
    const options = { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric',
        weekday: 'long'
    };
    return date.toLocaleDateString('ja-JP', options);
} 