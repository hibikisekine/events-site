// 今日行けるイベントサイト - JavaScript

let currentEvents = [];
let multiCityWeather = {};

// APIエンドポイント（静的JSONファイル使用）
const API_BASE = 'https://tsukuba.netlify.app/api';

// 地域リスト
const CITIES = [
    { name: 'つくば市', query: 'Tsukuba,Japan' },
    { name: 'つくばみらい市', query: 'Tsukubamirai,Japan' },
    { name: '取手市', query: 'Toride,Japan' },
    { name: '守谷市', query: 'Moriya,Japan' }
];

// ページ読み込み時の初期化
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 今日行けるイベントサイトを初期化中...');
    setupEventListeners();
    loadData();
});

// イベントリスナーの設定
function setupEventListeners() {
    // フィルター要素の取得
    const categoryFilter = document.getElementById('category-filter');
    const cityFilter = document.getElementById('city-filter');
    const locationFilter = document.getElementById('location-filter');
    const freeFilter = document.getElementById('free-filter');
    const childFriendlyFilter = document.getElementById('child-friendly-filter');
    const parkingFilter = document.getElementById('parking-filter');

    // フィルター変更時のイベント
    if (categoryFilter) categoryFilter.addEventListener('change', filterEvents);
    if (cityFilter) cityFilter.addEventListener('change', filterEvents);
    if (locationFilter) locationFilter.addEventListener('change', filterEvents);
    if (freeFilter) freeFilter.addEventListener('change', filterEvents);
    if (childFriendlyFilter) childFriendlyFilter.addEventListener('change', filterEvents);
    if (parkingFilter) parkingFilter.addEventListener('change', filterEvents);
}

// データ読み込み
async function loadData() {
    try {
        console.log('📊 データを読み込み中...');
        
        // 実際のスクレイピングデータを試行
        await loadScrapedEvents();
        
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
        <div class="event-card" onclick="showEventDetails(${event.id})">
            <div class="event-header">
                <h4 class="event-title">${escapeHtml(event.title)}</h4>
                <div class="event-badges">
                    ${event.is_free ? '<span class="badge bg-success">無料</span>' : '<span class="badge bg-warning">有料</span>'}
                    ${event.child_friendly ? '<span class="badge bg-info">子連れOK</span>' : ''}
                    ${event.has_parking ? '<span class="badge bg-secondary">駐車場</span>' : ''}
                    ${event.is_indoor ? '<span class="badge bg-primary">屋内</span>' : '<span class="badge bg-success">屋外</span>'}
                    <span class="badge bg-dark">${event.category}</span>
                    ${locationStr && locationStr.includes('市') ? `<span class="badge bg-info ms-2">${locationStr.match(/[^市]*市/)?.[0] || ''}</span>` : ''}
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
    if (linkElement) linkElement.href = event.url;
    
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
            </div>
            <div class="event-description-full">
                <h6>詳細</h6>
                <p>${escapeHtml(event.description || '詳細情報はありません')}</p>
            </div>
        `;
    }
    
    modal.show();
}

// データ更新
function refreshData() {
    console.log('🔄 データを更新中...');
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