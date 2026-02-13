"""
Enhanced Message Analyzer with Advanced NLP
Professional Telegram Message Analysis Engine
"""

import re
import json
from typing import Tuple, List, Optional, Dict, Any
from dataclasses import dataclass
from collections import Counter
import math
from config import config
from database import db


@dataclass
class AnalysisResult:
    """Enhanced analysis result structure"""
    is_help_request: bool
    services: List[str]
    confidence: float
    keywords_found: List[str]
    context_indicators: List[str]
    urgency_level: int  # 1-5 scale
    message_quality: float  # 0-1 quality score
    language_detected: str  # 'ar', 'en', 'mixed'
    original_text: str
    processed_text: str
    analysis_timestamp: str


class EnhancedMessageAnalyzer:
    """Advanced Message Analyzer with ML-like capabilities"""
    
    def __init__(self):
        # Enhanced service keywords with weights and variations
        self.service_keywords = config.SERVICE_KEYWORDS
        
        # Extended request patterns with weights
        self.request_patterns = [
            (r'محتاج.*مساعدة', 0.9),
            (r'من يساعدني', 0.85),
            (r'أحد يقدر.*يخدم', 0.8),
            (r'ممكن.*تساعد', 0.75),
            (r'عندكم.*?', 0.7),
            (r'من عنده.*?', 0.7),
            (r'أحد عنده.*?', 0.7),
            (r'هل يوجد.*?', 0.65),
            (r'أريد.*?', 0.8),
            (r'ابغى.*?', 0.8),
            (r'help me.*', 0.85),
            (r'need help.*', 0.8),
            (r'anyone can.*', 0.75),
            (r'looking for.*', 0.7)
        ]
        
        # Enhanced request indicators with categories
        self.request_indicators = {
            'direct_request': ['محتاج', 'أحتاج', 'أريد', 'ابغى', 'need', 'want'],
            'seeking_help': ['من يساعدني', 'ساعدني', 'ساعدوني', 'help me', 'help us'],
            'inquiring': ['عندكم', 'من عنده', 'هل يوجد', 'anyone has', 'does anyone'],
            'possibility': ['ممكن', 'أحد يقدر', 'can anyone', 'is it possible'],
            'urgency': ['عاجل', 'urgent', 'ضروري', '急需', 'emergency']
        }
        
        # Context and quality indicators
        self.context_indicators = {
            'academic': ['مادة', 'subject', 'class', 'grade', 'semester', 'فصل'],
            'professional': ['شركة', 'company', 'business', 'client', 'عمل'],
            'personal': ['لي', 'forme', 'myself', 'شخصي'],
            'group_related': ['الجروب', 'المجموعة', 'group', 'here']
        }
        
        # Negative/stop words that reduce confidence
        self.negative_indicators = [
            'شكراً', 'thanks', 'thank you', 'done', 'تم', 'finished', 
            'completed', 'resolved', 'حلها', 'انتهى'
        ]
        
        # Urgency keywords
        self.urgency_keywords = {
            5: ['عاجل', 'urgent', 'ضروري', 'emergency', 'مستعجل'],
            4: ['_today', 'اليوم', 'today', 'الليلة', 'tonight'],
            3: ['soon', 'قريباً', 'بسرعة', 'quickly'],
            2: ['tomorrow', 'غداً', 'next week', 'الأسبوع القادم'],
            1: ['later', 'لاحقاً', 'في المستقبل', ' eventual']
        }
        
    def clean_text(self, text: str) -> str:
        """Enhanced text cleaning with language detection"""
        if not text:
            return ""
        
        # Remove excessive punctuation while preserving meaning
        text = re.sub(r'[^\w\s\u0600-\u06FF\u0750-\u077F]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def detect_language(self, text: str) -> str:
        """Detect primary language (Arabic, English, or Mixed)"""
        arabic_chars = len(re.findall(r'[\u0600-\u06FF]', text))
        english_chars = len(re.findall(r'[a-zA-Z]', text))
        total_chars = arabic_chars + english_chars
        
        if total_chars == 0:
            return 'unknown'
        
        arabic_ratio = arabic_chars / total_chars
        
        if arabic_ratio > 0.7:
            return 'ar'
        elif arabic_ratio < 0.3:
            return 'en'
        else:
            return 'mixed'
    
    def calculate_message_quality(self, text: str) -> float:
        """Calculate message quality score (0-1)"""
        if not text:
            return 0.0
        
        # Length factor (optimal length 20-200 chars)
        length = len(text)
        if length < 10:
            length_score = 0.3
        elif 10 <= length <= 200:
            length_score = 1.0
        elif 200 < length <= 500:
            length_score = 0.8
        else:
            length_score = 0.5
        
        # Clarity factors
        sentences = re.split(r'[.!?،؛؟]+', text)
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
        
        # Reasonable sentence length (5-20 words ideal)
        clarity_score = 1.0 if 5 <= avg_sentence_length <= 20 else 0.7
        
        # Repetition check
        words = text.lower().split()
        if len(words) > 0:
            repetition_factor = len(set(words)) / len(words)
        else:
            repetition_factor = 0
        
        return (length_score * 0.4 + clarity_score * 0.4 + repetition_factor * 0.2)
    
    def extract_services(self, text: str) -> List[str]:
        """Enhanced service extraction with weighted scoring"""
        found_services = []
        text_lower = text.lower()
        
        for service, keywords in self.service_keywords.items():
            service_matches = []
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    service_matches.append(keyword)
            
            if service_matches:
                found_services.append({
                    'service': service,
                    'matches': service_matches,
                    'match_count': len(service_matches)
                })
        
        # Sort by match count and return service names
        sorted_services = sorted(found_services, key=lambda x: x['match_count'], reverse=True)
        return [item['service'] for item in sorted_services]
    
    def calculate_urgency(self, text: str) -> int:
        """Calculate urgency level (1-5)"""
        text_lower = text.lower()
        urgency_score = 1
        
        for level, keywords in self.urgency_keywords.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    urgency_score = max(urgency_score, level)
        
        return urgency_score
    
    def extract_context_indicators(self, text: str) -> List[str]:
        """Extract contextual information"""
        found_contexts = []
        text_lower = text.lower()
        
        for context_type, indicators in self.context_indicators.items():
            for indicator in indicators:
                if indicator.lower() in text_lower:
                    found_contexts.append(context_type)
                    break
        
        return list(set(found_contexts))
    
    def calculate_confidence(self, services: List[str], text: str, 
                           request_matches: int, context_indicators: List[str]) -> float:
        """Advanced confidence calculation"""
        if not services:
            return 0.0
        
        # Base confidence from service matches
        base_confidence = min(len(services) * 25, 75)
        
        # Boost from request pattern matches
        request_boost = min(request_matches * 15, 30)
        
        # Context relevance boost
        context_boost = len(context_indicators) * 10
        
        # Quality adjustment
        quality_factor = self.calculate_message_quality(text)
        
        # Language consistency bonus
        language = self.detect_language(text)
        language_bonus = 10 if language in ['ar', 'en'] else 5
        
        # Penalty for negative indicators
        text_lower = text.lower()
        negative_penalty = sum(10 for neg in self.negative_indicators if neg in text_lower)
        
        total_confidence = base_confidence + request_boost + context_boost + language_bonus - negative_penalty
        adjusted_confidence = total_confidence * quality_factor
        
        return min(max(adjusted_confidence, 0), 100)
    
    def analyze_message(self, text: str) -> AnalysisResult:
        """Enhanced comprehensive message analysis"""
        if not text or len(text) < 5:
            return AnalysisResult(
                is_help_request=False,
                services=[],
                confidence=0.0,
                keywords_found=[],
                context_indicators=[],
                urgency_level=1,
                message_quality=0.0,
                language_detected='unknown',
                original_text=text or "",
                processed_text="",
                analysis_timestamp=""
            )
        
        # Clean and process text
        processed_text = self.clean_text(text)
        language = self.detect_language(text)
        quality = self.calculate_message_quality(text)
        urgency = self.calculate_urgency(text)
        context_indicators = self.extract_context_indicators(text)
        
        # Extract services
        services = self.extract_services(text)
        
        # Find request patterns
        request_matches = 0
        matched_patterns = []
        
        for pattern, weight in self.request_patterns:
            if re.search(pattern, text.lower()):
                request_matches += 1
                matched_patterns.append(pattern)
        
        # Find request indicators
        found_indicators = []
        for category, indicators in self.request_indicators.items():
            for indicator in indicators:
                if indicator.lower() in text.lower():
                    found_indicators.append(f"{category}:{indicator}")
        
        # Calculate confidence
        confidence = self.calculate_confidence(services, text, request_matches, context_indicators)
        
        # Extract specific keywords found
        keywords_found = []
        text_lower = text.lower()
        for service_keywords in self.service_keywords.values():
            for keyword in service_keywords:
                if keyword.lower() in text_lower:
                    keywords_found.append(keyword)
        
        # Determine if it's a help request
        is_help_request = len(services) > 0 or request_matches > 0 or len(found_indicators) > 0
        if not is_help_request and confidence < config.CONFIDENCE_THRESHOLD:
            is_help_request = False
        
        return AnalysisResult(
            is_help_request=is_help_request,
            services=services,
            confidence=confidence,
            keywords_found=list(set(keywords_found)),
            context_indicators=context_indicators,
            urgency_level=urgency,
            message_quality=quality,
            language_detected=language,
            original_text=text,
            processed_text=processed_text,
            analysis_timestamp=""
        )
    
    def get_service_statistics(self, messages: List[str]) -> Dict[str, Any]:
        """Get statistics for service types in message collection"""
        service_counter = Counter()
        total_analyzed = 0
        help_requests = 0
        avg_confidence = 0
        
        for message in messages:
            result = self.analyze_message(message)
            total_analyzed += 1
            
            if result.is_help_request:
                help_requests += 1
                avg_confidence += result.confidence
                for service in result.services:
                    service_counter[service]
        
        return {
            'total_messages': total_analyzed,
            'help_requests': help_requests,
            'help_request_rate': (help_requests / total_analyzed * 100) if total_analyzed > 0 else 0,
            'average_confidence': (avg_confidence / help_requests) if help_requests > 0 else 0,
            'top_services': dict(service_counter.most_common(5))
        }


# Backward compatibility alias
MessageAnalyzer = EnhancedMessageAnalyzer

# Usage example
if __name__ == '__main__':
    analyzer = EnhancedMessageAnalyzer()
    
    # Test messages
    test_messages = [
        "السلام عليكم، محتاج مساعدة في واجب الرياضيات عاجل",
        "من عنده تقرير للفيزياء؟",
        "أحد يقدر يساعدني في مشروع التخرج ضروري",
        "ابغى تصميم بوستر لمشروعي اليوم",
        "مرحباً جميعاً، كيف حالكم؟",
        "Need help with presentation slides urgently!",
        "Looking for someone who can do my assignment"
    ]
    
    for msg in test_messages:
        result = analyzer.analyze_message(msg)
        print(f"\n{'='*50}")
        print(f"Message: {msg}")
        print(f"Help Request: {result.is_help_request}")
        print(f"Services: {result.services}")
        print(f"Confidence: {result.confidence:.1f}%")
        print(f"Urgency: Level {result.urgency_level}")
        print(f"Language: {result.language_detected}")
        print(f"Quality: {result.message_quality:.2f}")
        print(f"Keywords: {result.keywords_found}")
        print(f"Context: {result.context_indicators}")