// 今日行けるイベントサイト - JavaScript

let currentEvents = [];
let multiCityWeather = {};

// APIエンドポイント（静的JSONファイル使用）
const API_BASE = 'https://tsukuba.netlify.app/api';

// A8.net 広告クリック関数
function A8SalesClick() {
    console.log('🎯 A8.net 広告がクリックされました');
    // A8.netのスクリプトが読み込まれている場合、自動的に処理されます
    // クリックイベントのログを記録
    try {
        if (typeof window.A8SalesClick === 'function') {
            window.A8SalesClick();
        } else {
            console.log('📊 A8.net 広告クリックを記録');
            // 広告クリックの統計を記録（将来的な分析用）
            const clickData = {
                timestamp: new Date().toISOString(),
                type: 'ad_click',
                source: 'a8net'
            };
            console.log('📈 広告クリックデータ:', clickData);
        }
    } catch (error) {
        console.error('❌ A8.net 広告クリックエラー:', error);
    }
}

// Google Analytics イベント追跡
function trackEvent(eventName, eventCategory, eventAction, eventLabel = null) {
    if (typeof gtag !== 'undefined') {
        gtag('event', eventName, {
            event_category: eventCategory,
            event_action: eventAction,
            event_label: eventLabel
        });
    }
}

// ページビューの追跡
function trackPageView(pageTitle) {
    if (typeof gtag !== 'undefined') {
        gtag('config', 'G-BTJQ4YG2EP', {
            page_title: pageTitle,
            page_location: window.location.href
        });
    }
}

// 地域リスト
const CITIES = [
    { name: 'つくば市', query: 'Tsukuba,Japan' },
    { name: 'つくばみらい市', query: 'Tsukubamirai,Japan' },
    { name: '取手市', query: 'Toride,Japan' },
    { name: '守谷市', query: 'Moriya,Japan' }
];

// ページ読み込み時の初期化
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 ページ読み込み開始');
    
    // Google Analytics ページビューの追跡
    trackPageView('茨城県南のイベント情報');
    
    // データ読み込み
    loadData();
    
    // 忍者アドマックス 広告の初期化
    initializeNinjaAds();
    
    // フィルター機能の初期化
    initializeFilters();
    
    // 天気情報の取得
    getWeatherInfo();
    
    console.log('✅ ページ初期化完了');
});

// 忍者アドマックス 広告の初期化
function initializeNinjaAds() {
    console.log('🎯 忍者アドマックス 広告初期化開始');
    
    // 広告バナーの表示状態を確認
    checkAdBanners();
}

// 広告バナーの表示状態を確認
function checkAdBanners() {
    console.log('📢 忍者アドマックス広告の表示状態を確認中...');
    
    const adSections = document.querySelectorAll('.ad-section, .sidebar-ad');
    console.log(`📊 検出された広告セクション数: ${adSections.length}`);
    
    adSections.forEach((section, index) => {
        const isVisible = section.offsetParent !== null;
        const rect = section.getBoundingClientRect();
        console.log(`📢 広告${index + 1}: 表示=${isVisible}, 位置=(${rect.left}, ${rect.top}), サイズ=${rect.width}x${rect.height}`);
        
        // 広告バナーが見えない場合は警告を表示
        if (!isVisible || rect.width === 0 || rect.height === 0) {
            console.warn(`⚠️ 広告${index + 1}が表示されていません:`, section);
            section.style.border = '5px solid red';
            section.style.background = '#ffebee';
        }
    });
    
    // 忍者アドマックススクリプトの読み込み確認
    const ninjaScripts = document.querySelectorAll('script[src*="adm.shinobi.jp"]');
    console.log(`📊 忍者アドマックススクリプト数: ${ninjaScripts.length}`);
    ninjaScripts.forEach((script, index) => {
        console.log(`📊 忍者アドマックススクリプト${index + 1}: ${script.src}`);
    });
}



// イベントリスナーの設定
function setupEventListeners() {
    // フィルター要素の取得
    const categoryFilter = document.getElementById('category-filter');
    const cityFilter = document.getElementById('city-filter');
    const locationFilter = document.getElementById('location-filter');
    const freeFilter = document.getElementById('free-filter');
    const childFriendlyFilter = document.getElementById('child-friendly-filter');
    const parkingFilter = document.getElementById('parking-filter');

    // 地域特集フィルター要素の取得
    const contentCityFilter = document.getElementById('content-city-filter');
    const contentCategoryFilter = document.getElementById('content-category-filter');

    // 地域情報フィルター要素の取得
    const regionCityFilter = document.getElementById('region-city-filter');
    const regionCategoryFilter = document.getElementById('region-category-filter');

    // フィルター変更時のイベント
    if (categoryFilter) categoryFilter.addEventListener('change', () => {
        trackEvent('filter_change', 'engagement', 'filter', 'category');
        filterEvents();
    });
    if (cityFilter) cityFilter.addEventListener('change', () => {
        trackEvent('filter_change', 'engagement', 'filter', 'city');
        filterEvents();
    });
    if (locationFilter) locationFilter.addEventListener('change', () => {
        trackEvent('filter_change', 'engagement', 'filter', 'location');
        filterEvents();
    });
    if (freeFilter) freeFilter.addEventListener('change', () => {
        trackEvent('filter_change', 'engagement', 'filter', 'free');
        filterEvents();
    });
    if (childFriendlyFilter) childFriendlyFilter.addEventListener('change', () => {
        trackEvent('filter_change', 'engagement', 'filter', 'child_friendly');
        filterEvents();
    });
    if (parkingFilter) parkingFilter.addEventListener('change', () => {
        trackEvent('filter_change', 'engagement', 'filter', 'parking');
        filterEvents();
    });

    // 地域特集フィルター変更時のイベント
    if (contentCityFilter) contentCityFilter.addEventListener('change', () => {
        trackEvent('content_filter_change', 'engagement', 'filter', 'content_city');
        filterContent();
    });
    if (contentCategoryFilter) contentCategoryFilter.addEventListener('change', () => {
        trackEvent('content_filter_change', 'engagement', 'filter', 'content_category');
        filterContent();
    });

    // 地域情報フィルター変更時のイベント
    if (regionCityFilter) regionCityFilter.addEventListener('change', () => {
        trackEvent('region_filter_change', 'engagement', 'filter', 'region_city');
        filterRegion();
    });
    if (regionCategoryFilter) regionCategoryFilter.addEventListener('change', () => {
        trackEvent('region_filter_change', 'engagement', 'filter', 'region_category');
        filterRegion();
    });
}

// データ読み込み
async function loadData() {
    try {
        console.log('📊 データを読み込み中...');
        
        // 実際のスクレイピングデータを試行
        await loadScrapedEvents();
        
        // 新しいコンテンツデータを読み込み
        await loadContentData();
        
        // 複数地域の天気データの更新
        await loadMultiCityWeatherData();
        
        console.log('✅ データ読み込み完了');
    } catch (error) {
        console.error('❌ データ読み込みエラー:', error);
        // エラー時はサンプルデータを使用
        loadSampleData();
    }
}

// スクレイピングされたイベントデータを読み込み
async function loadScrapedEvents() {
    try {
        console.log('🔍 スクレイピングデータを取得中...');
        
        // 静的JSONファイルからデータを取得
        const response = await fetch(`${API_BASE}/events.json`);
        
        console.log('📡 APIレスポンス:', response.status, response.statusText);
        
        if (response.ok) {
            const data = await response.json();
            console.log('📊 取得したデータ:', data);
            
            if (data.events && data.events.length > 0) {
                console.log(`✅ スクレイピングデータを取得: ${data.events.length}件`);
                
                // データベースの形式に合わせて変換
                currentEvents = data.events.map(event => ({
                    id: event.id,
                    title: event.title,
                    date: event.date,
                    time: event.time,
                    location: event.location,
                    description: event.description,
                    category: event.category,
                    is_free: event.is_free,
                    has_parking: event.has_parking,
                    child_friendly: event.child_friendly,
                    is_indoor: event.is_indoor,
                    weather_dependent: event.weather_dependent,
                    rain_cancellation: event.rain_cancellation,
                    source_url: event.source_url,
                    source_city: event.source_city
                }));
                
                updateEventsDisplay();
                return;
            } else {
                console.log('⚠️ イベントデータが空です');
            }
        } else {
            console.log('❌ APIエラー:', response.status, response.statusText);
        }
        loadSampleData(); // Fallback to sample data
    } catch (error) {
        console.log('❌ スクレイピングデータ取得エラー:', error);
        loadSampleData();
    }
}

// 複数地域の天気データ読み込み
async function loadMultiCityWeatherData() {
    try {
        // WeatherAPIのキーを設定
        const API_KEY = '88ed0e701cfc4c7fb0d13301253107';
        
        // 各都市の天気データを並行して取得
        const weatherPromises = CITIES.map(async (city) => {
            try {
                const response = await fetch(`https://api.weatherapi.com/v1/current.json?key=${API_KEY}&q=${city.query}&aqi=no`);
                
                if (response.ok) {
                    const weatherData = await response.json();
                    return {
                        city: city.name,
                        data: {
                            temperature: Math.round(weatherData.current.temp_c),
                            condition: weatherData.current.condition.text,
                            humidity: weatherData.current.humidity,
                            rain_probability: weatherData.current.precip_mm > 0 ? Math.round(weatherData.current.precip_mm * 10) : 0,
                            icon: weatherData.current.condition.icon
                        }
                    };
                } else {
                    console.log(`⚠️ ${city.name}の天気データ取得エラー`);
                    return {
                        city: city.name,
                        data: {
                            temperature: '--',
                            condition: 'データ取得中',
                            humidity: '--',
                            rain_probability: 0,
                            icon: '113'
                        }
                    };
                }
            } catch (error) {
                console.log(`⚠️ ${city.name}の天気APIエラー:`, error);
                return {
                    city: city.name,
                    data: {
                        temperature: '--',
                        condition: 'データ取得中',
                        humidity: '--',
                        rain_probability: 0,
                        icon: '113'
                    }
                };
            }
        });
        
        const weatherResults = await Promise.all(weatherPromises);
        
        // 結果をオブジェクトに格納
        weatherResults.forEach(result => {
            multiCityWeather[result.city] = result.data;
        });
        
        console.log('✅ 複数地域の天気データを取得しました');
        
    } catch (error) {
        console.log('⚠️ 複数地域天気APIエラー、サンプルデータを使用:', error);
        loadSampleMultiCityWeatherData();
    }
    
    updateMultiCityWeatherDisplay();
}

// サンプル複数地域天気データ
function loadSampleMultiCityWeatherData() {
    multiCityWeather = {
        'つくば市': {
            temperature: 25,
            condition: '晴れ',
            humidity: 60,
            rain_probability: 10,
            icon: '113'
        },
        'つくばみらい市': {
            temperature: 24,
            condition: '曇り',
            humidity: 65,
            rain_probability: 20,
            icon: '116'
        },
        '取手市': {
            temperature: 26,
            condition: '晴れ',
            humidity: 55,
            rain_probability: 5,
            icon: '113'
        },
        '守谷市': {
            temperature: 23,
            condition: '小雨',
            humidity: 75,
            rain_probability: 40,
            icon: '296'
        }
    };
}

// 複数地域の天気表示更新
function updateMultiCityWeatherDisplay() {
    const weatherContainer = document.getElementById('weather-info');
    if (!weatherContainer) return;
    
    if (Object.keys(multiCityWeather).length === 0) {
        weatherContainer.innerHTML = `
            <div class="weather-details">
                <div class="weather-main">天気情報を取得中...</div>
                <div class="weather-temp">--°C</div>
                <div class="weather-humidity">湿度: --%</div>
                <div class="weather-rain">降水確率: --%</div>
            </div>
        `;
        return;
    }
    
    // 複数地域の天気を表示
    const weatherHTML = Object.entries(multiCityWeather).map(([city, weather]) => `
        <div class="city-weather">
            <div class="city-name">${city}</div>
            <div class="weather-icon">
                <img src="https:${weather.icon}" alt="${weather.condition}" width="32" height="32">
            </div>
            <div class="weather-details">
                <div class="weather-main">${weather.condition}</div>
                <div class="weather-temp">${weather.temperature}°C</div>
                <div class="weather-humidity">湿度: ${weather.humidity}%</div>
                <div class="weather-rain">降水確率: ${weather.rain_probability}%</div>
            </div>
        </div>
    `).join('');
    
    weatherContainer.innerHTML = `
        <div class="multi-city-weather">
            ${weatherHTML}
        </div>
    `;
}

// サンプルデータ読み込み
function loadSampleData() {
    const sampleEvents = [
        {
            id: 1,
            title: 'つくば市文化祭',
            date: '2025-08-15',
            time: '10:00',
            location: 'つくば市文化会館',
            description: 'つくば市の文化祭です。様々な展示やパフォーマンスがあります。',
            category: '文化',
            is_free: true,
            has_parking: true,
            child_friendly: true,
            is_indoor: true,
            url: 'https://example.com/event1'
        },
        {
            id: 2,
            title: '守谷市スポーツフェス',
            date: '2025-08-20',
            time: '14:00',
            location: '守谷市総合運動公園',
            description: '守谷市のスポーツイベントです。様々なスポーツ体験ができます。',
            category: 'スポーツ',
            is_free: false,
            has_parking: true,
            child_friendly: true,
            is_indoor: false,
            url: 'https://example.com/event2'
        },
        {
            id: 3,
            title: '子育てサポート講座',
            date: '2025-08-25',
            time: '13:30',
            location: '取手市子育て支援センター',
            description: '子育て中の方のためのサポート講座です。',
            category: '子育て',
            is_free: true,
            has_parking: true,
            child_friendly: true,
            is_indoor: true,
            url: 'https://example.com/event3'
        },
        {
            id: 4,
            title: 'つくばみらい市地域交流イベント',
            date: '2025-08-30',
            time: '11:00',
            location: 'つくばみらい市役所前広場',
            description: '地域の皆さんとの交流イベントです。',
            category: '地域',
            is_free: true,
            has_parking: true,
            child_friendly: true,
            is_indoor: false,
            url: 'https://example.com/event4'
        },
        {
            id: 5,
            title: '教育セミナー',
            date: '2025-09-05',
            time: '15:00',
            location: 'つくば市教育センター',
            description: '教育に関するセミナーです。',
            category: '教育',
            is_free: false,
            has_parking: true,
            child_friendly: false,
            is_indoor: true,
            url: 'https://example.com/event5'
        },
        {
            id: 6,
            title: '常総市農業体験',
            date: '2025-08-22',
            time: '09:00',
            location: '常総市農業公園',
            description: '農業体験イベントです。野菜の収穫体験ができます。',
            category: '地域',
            is_free: false,
            has_parking: true,
            child_friendly: true,
            is_indoor: false,
            url: 'https://example.com/event6'
        },
        {
            id: 7,
            title: '龍ヶ崎市音楽祭',
            date: '2025-08-28',
            time: '18:00',
            location: '龍ヶ崎市文化会館',
            description: '地元アーティストによる音楽祭です。',
            category: '文化',
            is_free: true,
            has_parking: true,
            child_friendly: true,
            is_indoor: true,
            url: 'https://example.com/event7'
        },
        {
            id: 8,
            title: '古河市歴史散策',
            date: '2025-09-10',
            time: '10:00',
            location: '古河市歴史博物館',
            description: '古河市の歴史を学ぶ散策イベントです。',
            category: '文化',
            is_free: true,
            has_parking: true,
            child_friendly: true,
            is_indoor: false,
            url: 'https://example.com/event8'
        },
        {
            id: 9,
            title: '坂東市スポーツ教室',
            date: '2025-08-18',
            time: '14:30',
            location: '坂東市体育館',
            description: '子供向けスポーツ教室です。',
            category: 'スポーツ',
            is_free: false,
            has_parking: true,
            child_friendly: true,
            is_indoor: true,
            url: 'https://example.com/event9'
        },
        {
            id: 10,
            title: 'つくば市科学実験教室',
            date: '2025-09-12',
            time: '13:00',
            location: 'つくば市科学館',
            description: '子供向け科学実験教室です。',
            category: '教育',
            is_free: false,
            has_parking: true,
            child_friendly: true,
            is_indoor: true,
            url: 'https://example.com/event10'
        },
        {
            id: 11,
            title: '守谷市フリーマーケット',
            date: '2025-08-24',
            time: '09:00',
            location: '守谷市中央公園',
            description: '地域のフリーマーケットです。',
            category: '地域',
            is_free: true,
            has_parking: true,
            child_friendly: true,
            is_indoor: false,
            url: 'https://example.com/event11'
        },
        {
            id: 12,
            title: '取手市子育て相談会',
            date: '2025-09-08',
            time: '10:00',
            location: '取手市子育て支援センター',
            description: '子育て相談会です。専門家が相談に応じます。',
            category: '子育て',
            is_free: true,
            has_parking: true,
            child_friendly: true,
            is_indoor: true,
            url: 'https://example.com/event12'
        }
    ];
    
    currentEvents = sampleEvents;
    updateEventsDisplay();
}

// フィルター適用
function filterEvents() {
    console.log('🔍 フィルター適用中...');
    
    const category = document.getElementById('category-filter')?.value || '';
    const city = document.getElementById('city-filter')?.value || '';
    const location = document.getElementById('location-filter')?.value || '';
    const freeOnly = document.getElementById('free-filter')?.checked || false;
    const childFriendly = document.getElementById('child-friendly-filter')?.checked || false;
    const parkingRequired = document.getElementById('parking-filter')?.checked || false;

    // フィルタリングロジック
    let filteredEvents = currentEvents.filter(event => {
        if (category && event.category !== category) return false;
        if (city && !event.location.includes(city)) return false;
        if (location === 'indoor' && !event.is_indoor) return false;
        if (location === 'outdoor' && event.is_indoor) return false;
        if (freeOnly && !event.is_free) return false;
        if (childFriendly && !event.child_friendly) return false;
        if (parkingRequired && !event.has_parking) return false;
        return true;
    });

    // 表示更新
    currentEvents = filteredEvents;
    updateEventsDisplay();
    
    console.log(`✅ フィルター適用完了: ${filteredEvents.length}件`);
}

// イベント表示更新
function updateEventsDisplay() {
    const container = document.getElementById('events-container');
    const countElement = document.getElementById('event-count');
    
    if (!container) return;
    
    // 件数更新
    if (countElement) {
        countElement.textContent = `${currentEvents.length}件`;
    }
    
    if (currentEvents.length === 0) {
        container.innerHTML = `
            <div class="alert alert-info">
                <i class="fas fa-info-circle me-2"></i>
                条件に合うイベントが見つかりませんでした。
            </div>
        `;
        return;
    }
    
    // イベントカード生成
    const eventsHTML = currentEvents.map(event => createEventCard(event)).join('');
    container.innerHTML = eventsHTML;
}

// イベントカード作成
function createEventCard(event) {
    const date = new Date(event.date);
    const formattedDate = date.toLocaleDateString('ja-JP', {
        month: 'long',
        day: 'numeric',
        weekday: 'short'
    });
    
    const timeStr = event.time ? event.time : '';
    const locationStr = event.location || '場所未定';
    const descriptionStr = event.description || '';
    
    return `
        <div class="event-card">
            <div class="event-header">
                <h4 class="event-title">${escapeHtml(event.title)}</h4>
                <div class="event-badges">
                    ${event.is_free ? '<span class="badge bg-success">無料</span>' : '<span class="badge bg-warning">有料</span>'}
                    ${event.child_friendly ? '<span class="badge bg-info">子連れOK</span>' : ''}
                    ${event.has_parking ? '<span class="badge bg-secondary">駐車場</span>' : ''}
                    ${event.is_indoor ? '<span class="badge bg-primary">屋内</span>' : '<span class="badge bg-success">屋外</span>'}
                    <span class="badge bg-dark">${event.category}</span>
                    ${event.source_city ? `<span class="badge bg-info ms-2">${event.source_city}</span>` : ''}
                </div>
            </div>
            <div class="event-details">
                <div class="event-date">
                    <i class="fas fa-calendar me-1"></i>
                    ${formattedDate} ${timeStr}
                </div>
                <div class="event-location">
                    <i class="fas fa-map-marker-alt me-1"></i>
                    ${escapeHtml(locationStr)}
                </div>
                <div class="event-description">
                    ${escapeHtml(descriptionStr.substring(0, 150))}${descriptionStr.length > 150 ? '...' : ''}
                </div>
            </div>
            <div class="event-actions">
                <button class="btn btn-outline-primary btn-sm" onclick="showEventDetails(${event.id})">
                    <i class="fas fa-info-circle me-1"></i>詳細を見る
                </button>
                ${event.source_url ? `<a href="${event.source_url}" class="btn btn-primary btn-sm ms-2" target="_blank">
                    <i class="fas fa-external-link-alt me-1"></i>公式サイト
                </a>` : ''}
            </div>
        </div>
    `;
}

// イベント詳細表示
function showEventDetails(eventId) {
    const event = currentEvents.find(e => e.id === eventId);
    if (!event) return;
    
    const modal = new bootstrap.Modal(document.getElementById('eventModal'));
    const titleElement = document.getElementById('eventModalTitle');
    const bodyElement = document.getElementById('eventModalBody');
    const linkElement = document.getElementById('eventModalLink');
    
    if (titleElement) titleElement.textContent = event.title;
    if (linkElement) linkElement.href = event.source_url || '#';
    
    if (bodyElement) {
        const date = new Date(event.date);
        const formattedDate = date.toLocaleDateString('ja-JP', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            weekday: 'long'
        });
        
        bodyElement.innerHTML = `
            <div class="event-detail-info">
                <p><strong>日時:</strong> ${formattedDate} ${event.time || ''}</p>
                <p><strong>場所:</strong> ${escapeHtml(event.location || '場所未定')}</p>
                <p><strong>カテゴリ:</strong> ${escapeHtml(event.category || 'カテゴリ未定')}</p>
                <p><strong>料金:</strong> ${event.is_free ? '無料' : '有料'}</p>
                <p><strong>駐車場:</strong> ${event.has_parking ? 'あり' : 'なし'}</p>
                <p><strong>子連れ:</strong> ${event.child_friendly ? 'OK' : '要確認'}</p>
                <p><strong>屋内/屋外:</strong> ${event.is_indoor ? '屋内' : '屋外'}</p>
                ${event.weather_dependent ? `<p><strong>天候依存:</strong> はい</p>` : ''}
                ${event.rain_cancellation ? `<p><strong>雨天時:</strong> ${escapeHtml(event.rain_cancellation)}</p>` : ''}
                ${event.source_city ? `<p><strong>地域:</strong> ${escapeHtml(event.source_city)}</p>` : ''}
            </div>
            <div class="event-description-full">
                <h6>詳細</h6>
                <p>${escapeHtml(event.description || '詳細情報はありません')}</p>
            </div>
        `;
    }
    
    // Google Analytics イベント追跡
    trackEvent('event_detail_view', 'engagement', 'view', event.title);
    
    modal.show();
}

// データ更新
function refreshData() {
    console.log('🔄 データを更新中...');
    trackEvent('data_refresh', 'engagement', 'click', 'refresh_button');
    loadData();
}

// エラー表示
function showError(message) {
    const container = document.getElementById('events-container');
    if (container) {
        container.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle me-2"></i>
                ${escapeHtml(message)}
            </div>
        `;
    }
}

// HTMLエスケープ
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// 新しいコンテンツデータを読み込み
async function loadContentData() {
    try {
        console.log('📚 コンテンツデータを読み込み中...');
        
        const response = await fetch(`${API_BASE}/content.json`);
        
        if (response.ok) {
            const data = await response.json();
            console.log('📊 コンテンツデータ:', data);
            
            // 各コンテンツセクションを更新
            updateSeasonalEvents(data.seasonal_events || []);
            updateFoodInfo(data.food_info || []);
            updateChildcareInfo(data.childcare_info || []);
            updateTourismInfo(data.tourism_info || []);
            updateCultureInfo(data.culture_info || []);
            
            console.log('✅ コンテンツデータ読み込み完了');
        } else {
            console.warn('⚠️ コンテンツデータの取得に失敗');
        }
    } catch (error) {
        console.error('❌ コンテンツデータ読み込みエラー:', error);
    }
}

// 地域特集フィルター機能
function filterContent() {
    const cityFilter = document.getElementById('content-city-filter').value;
    const categoryFilter = document.getElementById('content-category-filter').value;
    
    console.log('🔍 地域特集フィルター適用:', { city: cityFilter, category: categoryFilter });
    
    // 地域特集セクション内のコンテンツカードのみを対象
    const contentSection = document.querySelector('.content-section:has(.content-card[data-category="季節イベント"])');
    if (!contentSection) return;
    
    const contentCards = contentSection.querySelectorAll('.content-card');
    
    contentCards.forEach(card => {
        const category = card.getAttribute('data-category');
        const container = card.querySelector('[id$="-container"]');
        
        // カテゴリフィルター
        const categoryMatch = !categoryFilter || category === categoryFilter;
        
        // 地域フィルター（コンテンツ内のアイテムをチェック）
        let cityMatch = !cityFilter;
        if (cityFilter && container) {
            const items = container.querySelectorAll('.content-item');
            items.forEach(item => {
                const cityBadge = item.querySelector('.content-badge.city');
                if (cityBadge && cityBadge.textContent === cityFilter) {
                    cityMatch = true;
                }
            });
        }
        
        // 表示/非表示の切り替え
        if (categoryMatch && cityMatch) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
    
    // コンテンツ内のアイテムもフィルター
    if (cityFilter) {
        const contentItems = contentSection.querySelectorAll('.content-item');
        contentItems.forEach(item => {
            const cityBadge = item.querySelector('.content-badge.city');
            if (cityBadge) {
                if (cityBadge.textContent === cityFilter) {
                    item.style.display = 'block';
                } else {
                    item.style.display = 'none';
                }
            }
        });
    }
}

// 地域情報フィルター機能
function filterRegion() {
    const cityFilter = document.getElementById('region-city-filter').value;
    const categoryFilter = document.getElementById('region-category-filter').value;
    
    console.log('🔍 地域情報フィルター適用:', { city: cityFilter, category: categoryFilter });
    
    // 地域情報セクション内のコンテンツカードのみを対象
    const regionSection = document.querySelector('.content-section:has(.content-card[data-category="観光"])');
    if (!regionSection) return;
    
    const contentCards = regionSection.querySelectorAll('.content-card');
    
    contentCards.forEach(card => {
        const category = card.getAttribute('data-category');
        const container = card.querySelector('[id$="-container"]');
        
        // カテゴリフィルター
        const categoryMatch = !categoryFilter || category === categoryFilter;
        
        // 地域フィルター（コンテンツ内のアイテムをチェック）
        let cityMatch = !cityFilter;
        if (cityFilter && container) {
            const items = container.querySelectorAll('.content-item');
            items.forEach(item => {
                const cityBadge = item.querySelector('.content-badge.city');
                if (cityBadge && cityBadge.textContent === cityFilter) {
                    cityMatch = true;
                }
            });
        }
        
        // 表示/非表示の切り替え
        if (categoryMatch && cityMatch) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
    
    // コンテンツ内のアイテムもフィルター
    if (cityFilter) {
        const contentItems = regionSection.querySelectorAll('.content-item');
        contentItems.forEach(item => {
            const cityBadge = item.querySelector('.content-badge.city');
            if (cityBadge) {
                if (cityBadge.textContent === cityFilter) {
                    item.style.display = 'block';
                } else {
                    item.style.display = 'none';
                }
            }
        });
    }
}

// 季節イベントの表示を更新
function updateSeasonalEvents(events) {
    const container = document.getElementById('seasonal-events-container');
    if (!container) return;
    
    if (events.length === 0) {
        container.innerHTML = '<p class="text-muted">現在、季節イベントの情報はありません。</p>';
        return;
    }
    
    container.innerHTML = events.map(event => `
        <div class="content-item">
            <h5>${escapeHtml(event.title)}</h5>
            <p>${escapeHtml(event.description)}</p>
            <div class="content-meta">
                ${event.date ? `<span class="content-badge date">${event.date}</span>` : ''}
                ${event.location ? `<span class="content-badge">${escapeHtml(event.location)}</span>` : ''}
                ${event.category ? `<span class="content-badge category">${escapeHtml(event.category)}</span>` : ''}
                ${event.city ? `<span class="content-badge city">${escapeHtml(event.city)}</span>` : ''}
                ${event.source_url ? `<a href="${event.source_url}" class="content-link" target="_blank">詳細を見る</a>` : ''}
            </div>
        </div>
    `).join('');
}

// グルメ情報の表示を更新
function updateFoodInfo(foodInfo) {
    const container = document.getElementById('food-info-container');
    if (!container) return;
    
    if (foodInfo.length === 0) {
        container.innerHTML = '<p class="text-muted">現在、グルメ情報はありません。</p>';
        return;
    }
    
    container.innerHTML = foodInfo.map(food => `
        <div class="content-item">
            <h5>${escapeHtml(food.title)}</h5>
            <p>${escapeHtml(food.description)}</p>
            <div class="content-meta">
                ${food.location ? `<span class="content-badge">${escapeHtml(food.location)}</span>` : ''}
                ${food.category ? `<span class="content-badge category">${escapeHtml(food.category)}</span>` : ''}
                ${food.city ? `<span class="content-badge city">${escapeHtml(food.city)}</span>` : ''}
                ${food.source_url ? `<a href="${food.source_url}" class="content-link" target="_blank">詳細を見る</a>` : ''}
            </div>
        </div>
    `).join('');
}

// 子育て情報の表示を更新
function updateChildcareInfo(childcareInfo) {
    const container = document.getElementById('childcare-info-container');
    if (!container) return;
    
    if (childcareInfo.length === 0) {
        container.innerHTML = '<p class="text-muted">現在、子育て情報はありません。</p>';
        return;
    }
    
    container.innerHTML = childcareInfo.map(childcare => `
        <div class="content-item">
            <h5>${escapeHtml(childcare.title)}</h5>
            <p>${escapeHtml(childcare.description)}</p>
            <div class="content-meta">
                ${childcare.date ? `<span class="content-badge date">${childcare.date}</span>` : ''}
                ${childcare.location ? `<span class="content-badge">${escapeHtml(childcare.location)}</span>` : ''}
                ${childcare.category ? `<span class="content-badge category">${escapeHtml(childcare.category)}</span>` : ''}
                ${childcare.city ? `<span class="content-badge city">${escapeHtml(childcare.city)}</span>` : ''}
                ${childcare.source_url ? `<a href="${childcare.source_url}" class="content-link" target="_blank">詳細を見る</a>` : ''}
            </div>
        </div>
    `).join('');
}

// 観光情報の表示を更新
function updateTourismInfo(tourismInfo) {
    const container = document.getElementById('tourism-info-container');
    if (!container) return;
    
    if (tourismInfo.length === 0) {
        container.innerHTML = '<p class="text-muted">現在、観光情報はありません。</p>';
        return;
    }
    
    container.innerHTML = tourismInfo.map(tourism => `
        <div class="content-item">
            <h5>${escapeHtml(tourism.title)}</h5>
            <p>${escapeHtml(tourism.description)}</p>
            <div class="content-meta">
                ${tourism.location ? `<span class="content-badge">${escapeHtml(tourism.location)}</span>` : ''}
                ${tourism.category ? `<span class="content-badge category">${escapeHtml(tourism.category)}</span>` : ''}
                ${tourism.city ? `<span class="content-badge city">${escapeHtml(tourism.city)}</span>` : ''}
                ${tourism.source_url ? `<a href="${tourism.source_url}" class="content-link" target="_blank">詳細を見る</a>` : ''}
            </div>
        </div>
    `).join('');
}

// 文化施設情報の表示を更新
function updateCultureInfo(cultureInfo) {
    const container = document.getElementById('culture-info-container');
    if (!container) return;
    
    if (cultureInfo.length === 0) {
        container.innerHTML = '<p class="text-muted">現在、文化施設情報はありません。</p>';
        return;
    }
    
    container.innerHTML = cultureInfo.map(culture => `
        <div class="content-item">
            <h5>${escapeHtml(culture.title)}</h5>
            <p>${escapeHtml(culture.description)}</p>
            <div class="content-meta">
                ${culture.date ? `<span class="content-badge date">${culture.date}</span>` : ''}
                ${culture.location ? `<span class="content-badge">${escapeHtml(culture.location)}</span>` : ''}
                ${culture.category ? `<span class="content-badge category">${escapeHtml(culture.category)}</span>` : ''}
                ${culture.city ? `<span class="content-badge city">${escapeHtml(culture.city)}</span>` : ''}
                ${culture.source_url ? `<a href="${culture.source_url}" class="content-link" target="_blank">詳細を見る</a>` : ''}
            </div>
        </div>
    `).join('');
} 

// フィルター機能の初期化
function initializeFilters() {
    console.log('🔍 フィルター機能初期化');
    
    // イベントフィルター
    const categoryFilter = document.getElementById('category-filter');
    const cityFilter = document.getElementById('city-filter');
    const locationFilter = document.getElementById('location-filter');
    
    if (categoryFilter) categoryFilter.addEventListener('change', () => {
        trackEvent('filter_change', 'engagement', 'filter', 'category');
        filterEvents();
    });
    
    if (cityFilter) cityFilter.addEventListener('change', () => {
        trackEvent('filter_change', 'engagement', 'filter', 'city');
        filterEvents();
    });
    
    if (locationFilter) locationFilter.addEventListener('change', () => {
        trackEvent('filter_change', 'engagement', 'filter', 'location');
        filterEvents();
    });
    
    // コンテンツフィルター
    const contentCityFilter = document.getElementById('content-city-filter');
    const contentCategoryFilter = document.getElementById('content-category-filter');
    
    if (contentCityFilter) contentCityFilter.addEventListener('change', () => {
        trackEvent('filter_change', 'engagement', 'filter', 'content_city');
        filterContent();
    });
    
    if (contentCategoryFilter) contentCategoryFilter.addEventListener('change', () => {
        trackEvent('filter_change', 'engagement', 'filter', 'content_category');
        filterContent();
    });
    
    // 地域情報フィルター
    const regionCityFilter = document.getElementById('region-city-filter');
    const regionCategoryFilter = document.getElementById('region-category-filter');
    
    if (regionCityFilter) regionCityFilter.addEventListener('change', () => {
        trackEvent('filter_change', 'engagement', 'filter', 'region_city');
        filterRegion();
    });
    
    if (regionCategoryFilter) regionCategoryFilter.addEventListener('change', () => {
        trackEvent('filter_change', 'engagement', 'filter', 'region_category');
        filterRegion();
    });
    
    console.log('✅ フィルター機能初期化完了');
} 

// 天気情報の取得
function getWeatherInfo() {
    console.log('🌤️ 天気情報を取得中...');
    
    // 天気APIから情報を取得
    fetch('https://api.openweathermap.org/data/2.5/weather?q=Tsukuba,JP&appid=YOUR_API_KEY&units=metric&lang=ja')
        .then(response => response.json())
        .then(data => {
            console.log('✅ 天気情報を取得しました:', data);
            updateWeatherDisplay(data);
        })
        .catch(error => {
            console.error('❌ 天気情報の取得に失敗しました:', error);
            // エラー時はサンプルデータを表示
            updateWeatherDisplay({
                weather: [{ description: '晴れ' }],
                main: { temp: 25, humidity: 60 },
                rain: { '1h': 0 }
            });
        });
}

// 天気表示の更新
function updateWeatherDisplay(data) {
    const weatherInfo = document.getElementById('weather-info');
    if (!weatherInfo) return;
    
    const temp = Math.round(data.main.temp);
    const humidity = data.main.humidity;
    const description = data.weather[0].description;
    const rainProb = data.rain ? Math.round(data.rain['1h'] * 100) : 0;
    
    weatherInfo.innerHTML = `
        <div class="weather-details">
            <div class="weather-main">${description}</div>
            <div class="weather-temp">${temp}°C</div>
            <div class="weather-humidity">湿度: ${humidity}%</div>
            <div class="weather-rain">降水確率: ${rainProb}%</div>
        </div>
    `;
    
    console.log('✅ 天気表示を更新しました');
} 