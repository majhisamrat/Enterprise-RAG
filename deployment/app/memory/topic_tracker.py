"""
Topic Tracker for Automatic Topic Detection.

Identifies and tracks the current topic of conversation.
Examples: Sales Revenue, Leave Policy, Financial Report, etc.
"""

import re
import logging
from typing import Optional, Dict, List, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class TopicCategory(Enum):
    """Common topic categories in enterprise RAG."""
    SALES = "sales"
    FINANCE = "finance"
    HR = "hr"
    LEGAL = "legal"
    OPERATIONS = "operations"
    ADMIN = "admin"
    TECHNICAL = "technical"
    UNKNOWN = "unknown"


class TopicTracker:
    """
    Automatically detects and tracks conversation topics.
    
    Uses keyword matching and patterns to identify topics.
    """
    
    # Topic keywords mapping
    TOPIC_KEYWORDS = {
        TopicCategory.SALES: [
            "sales", "revenue", "income", "earnings", "turnover",
            "quarterly", "q1", "q2", "q3", "q4", "monthly", "weekly",
            "forecast", "target", "goal", "performance", "top performer",
        ],
        TopicCategory.FINANCE: [
            "finance", "financial", "accounting", "budget", "expense",
            "profit", "loss", "balance sheet", "cash flow", "investment",
            "capital", "loan", "debt", "interest",
        ],
        TopicCategory.HR: [
            "hr", "human resources", "employee", "staff", "leave", "vacation",
            "holiday", "attendance", "payroll", "salary", "benefits", "recruitment",
            "onboarding", "performance", "appraisal", "training",
        ],
        TopicCategory.LEGAL: [
            "legal", "contract", "agreement", "terms", "conditions", "compliance",
            "regulation", "policy", "clause", "liability", "law", "court",
            "lawsuit", "patent", "trademark", "copyright",
        ],
        TopicCategory.OPERATIONS: [
            "operations", "process", "procedure", "workflow", "automation",
            "supply", "logistics", "inventory", "warehouse", "shipping",
            "delivery", "quality", "production",
        ],
    }
    
    # Document type patterns
    DOCUMENT_PATTERNS = {
        "Weekly Sales Report": [
            r"weekly\s+sales", r"sales\s+report", r"revenue\s+summary",
        ],
        "Monthly Financial Report": [
            r"monthly\s+financial", r"financial\s+report", r"accounting",
        ],
        "Leave Policy": [
            r"leave\s+policy", r"vacation\s+policy", r"holiday\s+policy",
            r"time\s+off", r"pto",
        ],
        "Employee Handbook": [
            r"employee\s+handbook", r"company\s+policy", r"employee\s+guide",
        ],
        "Meeting Notes": [
            r"meeting\s+notes", r"minutes", r"discussion",
        ],
        "Contract": [
            r"contract", r"agreement", r"terms\s+and\s+conditions",
        ],
    }
    
    def __init__(self):
        """Initialize topic tracker."""
        logger.debug("TopicTracker initialized")
    
    def detect_topic(self, text: str, user_id: Optional[str] = None, session_id: Optional[str] = None) -> Tuple[Optional[str], TopicCategory, float]:
        """
        Detect topic from text.
        
        Args:
            text: Text to analyze
            user_id: Unused (kept for backwards compatibility)
            session_id: Unused (kept for backwards compatibility)
            
        Returns:
            Tuple of (topic_name, category, confidence)
        """
        if not text:
            return None, TopicCategory.UNKNOWN, 0.0
        
        text_lower = text.lower()
        
        # First try document type detection
        doc_type, confidence = self._detect_document_type(text_lower)
        if doc_type and confidence > 0.7:
            category = self._categorize_document(doc_type)
            logger.debug(f"Detected topic via document: {doc_type} ({confidence:.2f})")
            return doc_type, category, confidence
        
        # Then try keyword-based category detection
        category, confidence = self._detect_category(text_lower)
        if confidence > 0.5:
            logger.debug(f"Detected category: {category.value} ({confidence:.2f})")
            return category.value, category, confidence
        
        return None, TopicCategory.UNKNOWN, 0.0
    
    def _detect_document_type(self, text: str) -> Tuple[Optional[str], float]:
        """Detect specific document type."""
        best_match = None
        best_score = 0.0
        
        for doc_type, patterns in self.DOCUMENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    score = 0.9  # High confidence for regex matches
                    if score > best_score:
                        best_score = score
                        best_match = doc_type
        
        return best_match, best_score
    
    def _detect_category(self, text: str) -> Tuple[TopicCategory, float]:
        """Detect topic category using keyword matching."""
        category_scores = {}
        words = set(text.split())
        
        for category, keywords in self.TOPIC_KEYWORDS.items():
            matches = sum(1 for kw in keywords if kw in text.lower())
            if matches > 0:
                # Score based on number of matches and keyword frequency
                score = matches / len(keywords)
                category_scores[category] = score
        
        if not category_scores:
            return TopicCategory.UNKNOWN, 0.0
        
        best_category = max(category_scores.items(), key=lambda x: x[1])
        return best_category[0], best_category[1]
    
    def _categorize_document(self, doc_type: str) -> TopicCategory:
        """Categorize a document type into a category."""
        doc_lower = doc_type.lower()
        
        if "sales" in doc_lower:
            return TopicCategory.SALES
        elif "financial" in doc_lower or "accounting" in doc_lower:
            return TopicCategory.FINANCE
        elif "leave" in doc_lower or "employee" in doc_lower or "hr" in doc_lower:
            return TopicCategory.HR
        elif "contract" in doc_lower or "legal" in doc_lower:
            return TopicCategory.LEGAL
        else:
            return TopicCategory.UNKNOWN
    
    def extract_entities(self, text: str, category: TopicCategory) -> Dict[str, str]:
        """
        Extract entities relevant to the topic.
        
        Args:
            text: Text to extract from
            category: Topic category for context
            
        Returns:
            Dictionary of entity_name -> value
        """
        entities = {}
        
        # Day/date extraction
        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        for day in days:
            if day in text.lower():
                entities["day"] = day.capitalize()
                break
        
        # Quarter extraction (Q1, Q2, Q3, Q4)
        quarters = ["q1", "q2", "q3", "q4"]
        for q in quarters:
            if q in text.lower():
                entities["quarter"] = q.upper()
                break
        
        # Month extraction
        months = ["january", "february", "march", "april", "may", "june",
                  "july", "august", "september", "october", "november", "december"]
        for month in months:
            if month in text.lower():
                entities["month"] = month.capitalize()
                break
        
        # Category-specific entity extraction
        if category == TopicCategory.SALES:
            # Extract any numbers that might be revenue
            amounts = re.findall(r"\$[\d,]+", text, re.IGNORECASE)
            if amounts:
                entities["amount"] = amounts[0]
        
        elif category == TopicCategory.HR:
            # Extract employee-related info
            role_keywords = ["manager", "developer", "engineer", "analyst", "designer"]
            for role in role_keywords:
                if role in text.lower():
                    entities["role"] = role.capitalize()
                    break
        
        logger.debug(f"Extracted {len(entities)} entities for {category.value}")
        return entities


# Global instance
_topic_tracker: Optional[TopicTracker] = None


def get_topic_tracker() -> TopicTracker:
    """Get or create global topic tracker."""
    global _topic_tracker
    if _topic_tracker is None:
        _topic_tracker = TopicTracker()
    return _topic_tracker
