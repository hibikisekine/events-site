from datetime import datetime, timedelta

class EventFilter:
    def __init__(self):
        self.weather_priority = {
            'rainy': ['indoor', 'rain_ok', 'light_rain_ok'],
            'sunny': ['outdoor', 'indoor', 'any'],
            'cloudy': ['any', 'indoor', 'outdoor']
        }
    
    def filter_events_by_weather(self, events, weather_data):
        """天気予報に基づいてイベントをフィルタリング"""
        filtered_events = []
        
        for event in events:
            event_date = event[3]  # date column
            weather_for_date = self.get_weather_for_date(weather_data, event_date)
            
            # 天気データがない場合はデフォルトスコアを使用
            if weather_for_date:
                suitability_score = self.calculate_suitability_score(event, weather_for_date)
                weather_info = weather_for_date
            else:
                # 天気データがない場合はベーススコアを使用
                suitability_score = self.calculate_base_score(event)
                weather_info = {'condition': '不明', 'temp': 20, 'humidity': 60}
            
            # スコアが高いイベントのみを追加（閾値を下げる）
            if suitability_score > 0.1:
                event_dict = self.convert_event_to_dict(event)
                event_dict['suitability_score'] = suitability_score
                event_dict['weather_info'] = weather_info
                filtered_events.append(event_dict)
        
        # スコア順にソート
        filtered_events.sort(key=lambda x: x['suitability_score'], reverse=True)
        
        return filtered_events
    
    def get_weather_for_date(self, weather_data, event_date):
        """特定の日付の天気情報を取得"""
        for forecast in weather_data['forecast']:
            if forecast['date'] == event_date:
                return forecast
        return None
    
    def calculate_suitability_score(self, event, weather_info):
        """イベントと天気の適合性スコアを計算"""
        score = 0.5  # ベーススコア
        
        # 屋内/屋外の判定
        is_indoor = event[7]  # is_indoor column
        is_rainy = weather_info.get('is_rainy', False)
        is_sunny = weather_info.get('is_sunny', False)
        
        # 天候依存性の判定
        weather_dependent = event[11]  # weather_dependent column
        rain_cancellation = event[12]  # rain_cancellation column
        
        # 屋内イベントのスコア調整
        if is_indoor:
            if is_rainy:
                score += 0.3  # 雨の日は屋内イベントが有利
            elif is_sunny:
                score += 0.1  # 晴れの日は屋内イベントもOK
        else:
            # 屋外イベントのスコア調整
            if is_rainy:
                if rain_cancellation == '雨でも開催':
                    score += 0.2
                elif rain_cancellation == '小雨決行':
                    score += 0.1
                else:
                    score -= 0.4  # 雨天中止の屋外イベントは不利
            elif is_sunny:
                score += 0.3  # 晴れの日は屋外イベントが有利
        
        # その他の要因によるスコア調整
        if event[8]:  # is_free
            score += 0.1  # 無料イベントは有利
        
        if event[10]:  # child_friendly
            score += 0.1  # 子連れOKは有利
        
        if event[9]:  # has_parking
            score += 0.05  # 駐車場ありは有利
        
        # 時間帯による調整
        event_time = event[4]  # time column
        if event_time:
            hour = int(event_time.split(':')[0])
            if 9 <= hour <= 17:  # 日中イベント
                score += 0.1
        
        return min(score, 1.0)  # 最大1.0に制限
    
    def calculate_base_score(self, event):
        """天気データがない場合のベーススコアを計算"""
        score = 0.5  # ベーススコア
        
        # その他の要因によるスコア調整
        if event[8]:  # is_free
            score += 0.1  # 無料イベントは有利
        
        if event[10]:  # child_friendly
            score += 0.1  # 子連れOKは有利
        
        if event[9]:  # has_parking
            score += 0.05  # 駐車場ありは有利
        
        # 時間帯による調整
        event_time = event[4]  # time column
        if event_time:
            try:
                hour = int(event_time.split(':')[0])
                if 9 <= hour <= 17:  # 日中イベント
                    score += 0.1
            except (ValueError, IndexError):
                pass
        
        return min(score, 1.0)  # 最大1.0に制限
    
    def convert_event_to_dict(self, event):
        """イベントデータを辞書形式に変換"""
        return {
            'id': event[0],
            'title': event[1],
            'description': event[2],
            'date': event[3],
            'time': event[4],
            'location': event[5],
            'category': event[6],
            'is_indoor': bool(event[7]),
            'is_free': bool(event[8]),
            'has_parking': bool(event[9]),
            'child_friendly': bool(event[10]),
            'weather_dependent': bool(event[11]),
            'rain_cancellation': event[12],
            'source_url': event[13]
        }
    
    def get_recommended_events(self, events, weather_data, filters=None):
        """フィルター条件に基づいて推奨イベントを取得"""
        if not filters:
            filters = {}
        
        recommended = []
        
        for event in events:
            # フィルター条件をチェック
            if self.matches_filters(event, filters):
                event_date = event[3]
                weather_for_date = self.get_weather_for_date(weather_data, event_date)
                
                if weather_for_date:
                    suitability_score = self.calculate_suitability_score(event, weather_for_date)
                    
                    if suitability_score > 0.4:  # より厳しい条件
                        event_dict = self.convert_event_to_dict(event)
                        event_dict['suitability_score'] = suitability_score
                        event_dict['weather_info'] = weather_for_date
                        event_dict['recommendation_reason'] = self.get_recommendation_reason(event, weather_for_date)
                        recommended.append(event_dict)
        
        # スコア順にソート
        recommended.sort(key=lambda x: x['suitability_score'], reverse=True)
        
        return recommended[:10]  # 上位10件を返す
    
    def matches_filters(self, event, filters):
        """フィルター条件にマッチするかチェック"""
        if not filters:
            return True
        
        # 屋内/屋外フィルター
        if filters.get('indoor_only') and not event[7]:  # is_indoor
            return False
        
        if filters.get('outdoor_only') and event[7]:  # is_indoor
            return False
        
        # 無料イベントフィルター
        if filters.get('free_only') and not event[8]:  # is_free
            return False
        
        # 子連れOKフィルター
        if filters.get('child_friendly') and not event[10]:  # child_friendly
            return False
        
        # 駐車場ありフィルター
        if filters.get('parking_required') and not event[9]:  # has_parking
            return False
        
        # カテゴリフィルター
        if filters.get('category') and event[6] != filters['category']:  # category
            return False
        
        return True
    
    def get_recommendation_reason(self, event, weather_info):
        """推奨理由を生成"""
        reasons = []
        
        is_indoor = event[7]
        is_rainy = weather_info.get('is_rainy', False)
        is_sunny = weather_info.get('is_sunny', False)
        
        if is_indoor and is_rainy:
            reasons.append("雨の日なので屋内イベントがおすすめ")
        elif not is_indoor and is_sunny:
            reasons.append("晴れの日なので屋外イベントがおすすめ")
        elif event[8]:  # is_free
            reasons.append("無料で参加できます")
        elif event[10]:  # child_friendly
            reasons.append("お子様連れでも安心")
        elif event[9]:  # has_parking
            reasons.append("駐車場完備")
        
        if not reasons:
            reasons.append("天候に適したイベントです")
        
        return "、".join(reasons)
    
    def get_weather_summary(self, weather_data):
        """天気の概要を生成"""
        today_weather = None
        for forecast in weather_data['forecast']:
            if forecast['date'] == datetime.now().strftime('%Y-%m-%d'):
                today_weather = forecast
                break
        
        if not today_weather:
            return "天気情報が取得できませんでした"
        
        summary = f"今日の天気: {today_weather['description']}"
        summary += f"、気温: {today_weather['temperature']}°C"
        
        if today_weather.get('is_rainy'):
            summary += "、雨の予報です。屋内イベントがおすすめです。"
        elif today_weather.get('is_sunny'):
            summary += "、晴れの予報です。屋外イベントも楽しめます。"
        else:
            summary += "、曇りの予報です。"
        
        return summary 