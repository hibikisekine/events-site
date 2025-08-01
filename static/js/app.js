// 今日行けるイベントサイト - JavaScript

let currentEvents = [];
let currentWeather = null;

// APIエンドポイント（Netlify用）
const API_BASE = 'https://tsukuba.netlify.app/api';

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
        
        // サンプルデータを使用（APIがない場合）
        loadSampleData();
        
        // 天気データの更新
        await loadWeatherData();
        
        console.log('✅ データ読み込み完了');
    } catch (error) {
        console.error('❌ データ読み込みエラー:', error);
        showError('データの読み込みに失敗しました');
    }
}

// 天気データ読み込み
async function loadWeatherData() {
    try {
        // 実際のAPIキーを設定してください
        const API_KEY = 'YOUR_OPENWEATHER_API_KEY'; // ここに実際のAPIキーを入力
        
        // つくば市の天気データを取得
        const response = await fetch(`https://api.openweathermap.org/data/2.5/weather?q=Tsukuba,JP&appid=${API_KEY}&units=metric&lang=ja`);
        
        if (response.ok) {
            const weatherData = await response.json();
            currentWeather = {
                current: {
                    temperature: Math.round(weatherData.main.temp),
                    condition: weatherData.weather[0].description,
                    humidity: weatherData.main.humidity,
                    rain_probability: weatherData.rain ? Math.round(weatherData.rain['1h'] * 100) : 0
                },
                forecast: [
                    {
                        date: new Date().toISOString().split('T')[0],
                        condition: weatherData.weather[0].description,
                        temperature: Math.round(weatherData.main.temp),
                        humidity: weatherData.main.humidity,
                        rain_probability: weatherData.rain ? Math.round(weatherData.rain['1h'] * 100) : 0
                    }
                ]
            };
            console.log('✅ 実際の天気データを取得しました');
        } else {
            console.log('⚠️ 天気APIエラー、サンプルデータを使用');
            loadSampleWeatherData();
        }
    } catch (error) {
        console.log('⚠️ 天気APIエラー、サンプルデータを使用:', error);
        loadSampleWeatherData();
    }
    
    updateWeatherDisplay();
}

// サンプル天気データ
function loadSampleWeatherData() {
    currentWeather = {
        current: {
            temperature: 25,
            condition: '晴れ',
            humidity: 60,
            rain_probability: 10
        },
        forecast: [
            {
                date: new Date().toISOString().split('T')[0],
                condition: '晴れ',
                temperature: 25,
                humidity: 60,
                rain_probability: 10
            }
        ]
    };
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

// 天気表示更新
function updateWeatherDisplay() {
    const weatherInfo = document.getElementById('weather-info');
    const weatherIcon = document.getElementById('weather-icon');
    
    if (!weatherInfo || !weatherIcon) return;
    
    if (!currentWeather) {
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
    
    const today = new Date().toISOString().split('T')[0];
    const todayWeather = currentWeather.forecast ? currentWeather.forecast.find(f => f.date === today) : null;
    
    if (todayWeather) {
        weatherInfo.innerHTML = `
            <div class="weather-details">
                <div class="weather-main">${todayWeather.condition || '晴れ'}</div>
                <div class="weather-temp">${todayWeather.temperature || '--'}°C</div>
                <div class="weather-humidity">湿度: ${todayWeather.humidity || '--'}%</div>
                <div class="weather-rain">降水確率: ${Math.round(todayWeather.rain_probability || 0)}%</div>
            </div>
        `;
        updateWeatherIcon(weatherIcon, todayWeather);
    } else {
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

// 天気アイコン更新
function updateWeatherIcon(iconElement, weather) {
    const condition = weather.condition || '';
    const isRainy = condition.includes('雨') || condition.includes('雪');
    const isCloudy = condition.includes('曇');
    
    if (isRainy) {
        iconElement.innerHTML = '<i class="fas fa-cloud-rain fa-3x text-info"></i>';
    } else if (isCloudy) {
        iconElement.innerHTML = '<i class="fas fa-cloud fa-3x text-secondary"></i>';
    } else {
        iconElement.innerHTML = '<i class="fas fa-sun fa-3x text-warning"></i>';
    }
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