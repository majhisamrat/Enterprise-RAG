"""
PHASE 1: Schema Discovery Engine

Detects semantic column roles from CSV/XLSX data:
- Column name analysis (fuzzy matching against known patterns)
- Data type inference (numeric, date, categorical, text)
- Value shape analysis (cardinality, NULL%, range)
- Optional LLM classification for ambiguous columns

Output: Per-column metadata with semantic role + confidence score
"""

import re
from typing import Any, Dict, List, Optional, Set, Tuple
from datetime import datetime
from enum import Enum
import pandas as pd
import numpy as np
from app.utils.logger import logger


class SemanticRole(str, Enum):
    """Canonical semantic roles for CSV columns."""
    # Identity
    IDENTITY = "identity"  # id, transaction_id, order_id, customer_id, product_id
    
    # Temporal
    DATE = "date"  # transaction_date, order_date, invoice_date, created_at
    TIME = "time"  # created_time, updated_time
    DATETIME = "datetime"  # timestamp columns
    
    # Entity/Categorical
    ENTITY = "entity"  # product, category, customer, vendor, region
    
    # Quantity/Numeric
    QUANTITY = "quantity"  # quantity, units, units_sold, number_of_items
    
    # Financial
    REVENUE = "revenue"  # revenue, sales, sales_amount, total_sales
    COST = "cost"  # cost, production_cost, unit_cost
    PRICE = "price"  # price, unit_price, selling_price
    PROFIT = "profit"  # profit, gross_profit, net_profit
    DISCOUNT = "discount"  # discount, discount_percent, discount_amount
    TAX = "tax"  # tax, sales_tax, tax_amount
    
    # Location
    COUNTRY = "country"  # country, country_name
    STATE = "state"  # state, province, region
    CITY = "city"  # city, city_name
    REGION = "region"  # region, territory, area
    
    # Other
    RATING = "rating"  # rating, score, grade, rank
    STATUS = "status"  # status, state, type, category
    PERCENTAGE = "percentage"  # percentage, percent, rate
    
    # Unknown/Unmapped
    UNKNOWN = "unknown"


class ColumnMetadata:
    """Metadata for a single column."""
    
    def __init__(
        self,
        original_name: str,
        normalized_name: str,
        data_type: str,
        semantic_role: SemanticRole,
        confidence: float,
        null_percentage: float,
        sample_values: List[Any],
        unique_count: int,
        min_value: Optional[Any] = None,
        max_value: Optional[Any] = None,
        possible_roles: Optional[List[SemanticRole]] = None,
        notes: Optional[str] = None,
    ):
        self.original_name = original_name
        self.normalized_name = normalized_name
        self.data_type = data_type
        self.semantic_role = semantic_role
        self.confidence = confidence
        self.null_percentage = null_percentage
        self.sample_values = sample_values
        self.unique_count = unique_count
        self.min_value = min_value
        self.max_value = max_value
        self.possible_roles = possible_roles or []
        self.notes = notes
        self.status = "MAPPED" if confidence >= 0.85 else "AMBIGUOUS_SCHEMA"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "original_name": self.original_name,
            "normalized_name": self.normalized_name,
            "data_type": self.data_type,
            "semantic_role": self.semantic_role.value,
            "confidence": self.confidence,
            "null_percentage": self.null_percentage,
            "sample_values": [str(v) if v is not None else None for v in self.sample_values],
            "unique_count": self.unique_count,
            "min_value": str(self.min_value) if self.min_value is not None else None,
            "max_value": str(self.max_value) if self.max_value is not None else None,
            "possible_roles": [r.value for r in self.possible_roles],
            "notes": self.notes,
            "status": self.status,
        }


class SchemaDiscoveryEngine:
    """
    Discovers semantic schema from CSV/XLSX data.
    
    Strategy:
    1. Deterministic signals (column name patterns, dtype, value distribution)
    2. If confidence < 0.85: mark as AMBIGUOUS, list candidates
    3. Do NOT guess or block ingestion
    4. Optional LLM escalation for future enhancement
    """
    
    # Pattern mappings for semantic roles
    IDENTITY_PATTERNS = [
        r"\b(id|identifier|uid|uuid|pk|primary_key)\b",
        r"(transaction|order|invoice|customer|product|user)_id\b",
        r"^id$",
    ]
    
    DATE_PATTERNS = [
        r"(date|day)\b",
        r"(_date|_day)$",
        r"(transaction|order|invoice|created|updated|published|start|end)_date\b",
        r"^(date|day)$",
    ]
    
    TIME_PATTERNS = [
        r"(time|hour|minute|second)\b",
        r"(_time)$",
        r"(created|updated|started|ended)_time\b",
    ]
    
    QUANTITY_PATTERNS = [
        r"\b(quantity|units|qty|count|amount|number|volume|items?)\b",
        r"(units|qty|quantity)(_sold|_ordered|_purchased)?\b",
        r"^(qty|units|quantity)$",
    ]
    
    REVENUE_PATTERNS = [
        r"\b(revenue|sales|turnover|income|gross_revenue|net_revenue)\b",
        r"(sales|revenue|turnover)_amount\b",
        r"total_(sales|revenue)\b",
        r"^(revenue|sales)$",
    ]
    
    COST_PATTERNS = [
        r"\b(cost|expense|cogs|production_cost|unit_cost)\b",
        r"(cost|expense)_(total|amount|per_unit)?\b",
        r"^cost$",
    ]
    
    PRICE_PATTERNS = [
        r"\b(price|cost|rate|charge|amount)\b",
        r"(unit_)?price\b",
        r"(selling|list|unit|average)_price\b",
        r"^price$",
    ]
    
    PROFIT_PATTERNS = [
        r"\b(profit|earnings|income|net_income|gross_profit)\b",
        r"^profit$",
    ]
    
    DISCOUNT_PATTERNS = [
        r"\b(discount|reduction|rebate)\b",
        r"(discount|reduction)_(percent|amount|rate)?\b",
        r"^discount$",
    ]
    
    TAX_PATTERNS = [
        r"\b(tax|taxation)\b",
        r"(sales_)?tax_(amount|rate|percent)?\b",
        r"^tax$",
    ]
    
    COUNTRY_PATTERNS = [
        r"\b(country|nation|state)\b",
        r"country(_name|_code)?\b",
        r"^country$",
    ]
    
    STATE_PATTERNS = [
        r"\b(state|province|region|territory)\b",
        r"^(state|province|region)$",
    ]
    
    CITY_PATTERNS = [
        r"\b(city|town|municipality)\b",
        r"city(_name)?\b",
        r"^city$",
    ]
    
    REGION_PATTERNS = [
        r"\b(region|territory|area|zone|district)\b",
        r"^(region|territory|area)$",
    ]
    
    RATING_PATTERNS = [
        r"\b(rating|score|grade|rank|level)\b",
        r"(customer_|product_)?rating\b",
        r"^(rating|score)$",
    ]
    
    STATUS_PATTERNS = [
        r"\b(status|state|type|category|class)\b",
        r"(order_)?status\b",
        r"^(status|state|type)$",
    ]
    
    PERCENTAGE_PATTERNS = [
        r"\b(percent|percentage|rate|ratio)\b",
        r"(_)?percent(age|_)?\b",
        r"^(percent|percentage|rate)$",
    ]
    
    def __init__(self, confidence_threshold: float = 0.85):
        """
        Initialize schema discovery engine.
        
        Args:
            confidence_threshold: Minimum confidence for auto-mapping (0-1)
        """
        self.confidence_threshold = confidence_threshold
        self.role_patterns = {
            SemanticRole.IDENTITY: self.IDENTITY_PATTERNS,
            SemanticRole.DATE: self.DATE_PATTERNS,
            SemanticRole.TIME: self.TIME_PATTERNS,
            SemanticRole.QUANTITY: self.QUANTITY_PATTERNS,
            SemanticRole.REVENUE: self.REVENUE_PATTERNS,
            SemanticRole.COST: self.COST_PATTERNS,
            SemanticRole.PRICE: self.PRICE_PATTERNS,
            SemanticRole.PROFIT: self.PROFIT_PATTERNS,
            SemanticRole.DISCOUNT: self.DISCOUNT_PATTERNS,
            SemanticRole.TAX: self.TAX_PATTERNS,
            SemanticRole.COUNTRY: self.COUNTRY_PATTERNS,
            SemanticRole.STATE: self.STATE_PATTERNS,
            SemanticRole.CITY: self.CITY_PATTERNS,
            SemanticRole.REGION: self.REGION_PATTERNS,
            SemanticRole.RATING: self.RATING_PATTERNS,
            SemanticRole.STATUS: self.STATUS_PATTERNS,
            SemanticRole.PERCENTAGE: self.PERCENTAGE_PATTERNS,
        }
    
    def discover(self, dataframe: pd.DataFrame, sheet_name: Optional[str] = None) -> Dict[str, ColumnMetadata]:
        """
        Discover schema from pandas DataFrame.
        
        Args:
            dataframe: Input DataFrame
            sheet_name: Optional sheet name (for XLSX context)
        
        Returns:
            Dict mapping column names to ColumnMetadata
        """
        logger.info(f"Discovering schema for {len(dataframe.columns)} columns (sheet: {sheet_name or 'default'})")
        
        schema: Dict[str, ColumnMetadata] = {}
        
        for col_name in dataframe.columns:
            col_data = dataframe[col_name]
            
            # 1. Normalize column name
            normalized = self._normalize_name(col_name)
            
            # 2. Infer data type
            inferred_dtype = self._infer_dtype(col_data)
            
            # 3. Calculate statistics
            null_pct = (col_data.isnull().sum() / len(col_data)) * 100
            unique_count = col_data.nunique()
            sample_values = col_data.dropna().head(5).tolist()
            min_val, max_val = self._get_range(col_data, inferred_dtype)
            
            # 4. Detect semantic role
            role, confidence, possible_roles = self._detect_role(
                col_name, normalized, col_data, inferred_dtype
            )
            
            # 5. Create metadata
            metadata = ColumnMetadata(
                original_name=col_name,
                normalized_name=normalized,
                data_type=inferred_dtype,
                semantic_role=role,
                confidence=confidence,
                null_percentage=null_pct,
                sample_values=sample_values,
                unique_count=unique_count,
                min_value=min_val,
                max_value=max_val,
                possible_roles=possible_roles,
                notes=self._generate_notes(col_name, inferred_dtype, null_pct, unique_count),
            )
            
            schema[col_name] = metadata
            
            logger.debug(
                f"Column '{col_name}': {inferred_dtype} → {role.value} "
                f"(confidence: {confidence:.2f}, nulls: {null_pct:.1f}%)"
            )
        
        logger.success(f"Schema discovery complete: {len(schema)} columns")
        return schema
    
    def _normalize_name(self, name: str) -> str:
        """Normalize column name for comparison."""
        # Convert to lowercase, replace spaces/underscores with underscore
        normalized = re.sub(r'[\s\-]+', '_', name.lower().strip())
        # Remove leading/trailing underscores
        normalized = normalized.strip('_')
        return normalized
    
    def _infer_dtype(self, series: pd.Series) -> str:
        """Infer data type from pandas Series."""
        # Skip nulls
        non_null = series.dropna()
        if len(non_null) == 0:
            return "unknown"
        
        # Check pandas dtype first
        if pd.api.types.is_integer_dtype(series):
            return "integer"
        elif pd.api.types.is_float_dtype(series):
            return "float"
        elif pd.api.types.is_datetime64_any_dtype(series):
            return "datetime"
        elif pd.api.types.is_bool_dtype(series):
            return "boolean"
        
        # Heuristic: check first non-null value
        sample = non_null.iloc[0]
        
        # Try parsing as date
        if self._is_date_like(sample):
            return "date"
        
        # Try parsing as numeric
        try:
            float(sample)
            return "numeric"
        except (ValueError, TypeError):
            pass
        
        # Default to string
        return "string"
    
    def _is_date_like(self, value: Any) -> bool:
        """Check if value looks like a date."""
        if isinstance(value, (datetime, pd.Timestamp)):
            return True
        
        if not isinstance(value, str):
            return False
        
        value = str(value).strip()
        
        # Common date patterns
        date_patterns = [
            r'^\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'^\d{2}-\d{2}-\d{4}',  # MM-DD-YYYY or DD-MM-YYYY
            r'^\d{1,2}/\d{1,2}/\d{2,4}',  # MM/DD/YYYY
            r'^\d{4}/\d{1,2}/\d{1,2}',  # YYYY/MM/DD
        ]
        
        return any(re.match(p, value) for p in date_patterns)
    
    def _get_range(self, series: pd.Series, dtype: str) -> Tuple[Optional[Any], Optional[Any]]:
        """Get min/max values for numeric or date columns."""
        non_null = series.dropna()
        if len(non_null) == 0:
            return None, None
        
        if dtype in ("integer", "float", "numeric"):
            try:
                return float(non_null.min()), float(non_null.max())
            except (ValueError, TypeError):
                return None, None
        
        if dtype in ("date", "datetime"):
            try:
                return str(non_null.min()), str(non_null.max())
            except (ValueError, TypeError):
                return None, None
        
        return None, None
    
    def _detect_role(
        self,
        col_name: str,
        normalized_name: str,
        series: pd.Series,
        dtype: str,
    ) -> Tuple[SemanticRole, float, List[SemanticRole]]:
        """
        Detect semantic role from column signals.
        
        Returns:
            (primary_role, confidence, [possible_alternatives])
        """
        scores: Dict[SemanticRole, float] = {}
        
        # 1. Pattern matching on column name
        for role, patterns in self.role_patterns.items():
            for pattern in patterns:
                if re.search(pattern, col_name, re.IGNORECASE):
                    scores[role] = scores.get(role, 0) + 0.4
                    break
        
        # 2. Data type compatibility
        dtype_signals = self._dtype_signals(dtype)
        for role, score in dtype_signals.items():
            scores[role] = scores.get(role, 0) + score
        
        # 3. Value distribution signals
        dist_signals = self._distribution_signals(series, dtype)
        for role, score in dist_signals.items():
            scores[role] = scores.get(role, 0) + score
        
        # 4. Cardinality signals
        unique_pct = (series.nunique() / len(series)) * 100
        if unique_pct > 95:  # High cardinality → likely identity or text
            scores[SemanticRole.IDENTITY] = scores.get(SemanticRole.IDENTITY, 0) + 0.15
        elif unique_pct < 10:  # Low cardinality → likely category/status
            scores[SemanticRole.STATUS] = scores.get(SemanticRole.STATUS, 0) + 0.1
            scores[SemanticRole.ENTITY] = scores.get(SemanticRole.ENTITY, 0) + 0.05
        
        # 5. Find best match
        if not scores:
            return SemanticRole.UNKNOWN, 0.0, []
        
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        best_role, best_score = sorted_scores[0]
        
        # Normalize confidence to 0-1
        best_confidence = min(best_score, 1.0)
        
        # Collect alternatives (for ambiguous columns)
        alternatives = [role for role, score in sorted_scores[1:4] if score > 0.2]
        
        return best_role, best_confidence, alternatives
    
    def _dtype_signals(self, dtype: str) -> Dict[SemanticRole, float]:
        """Signal scores based on data type."""
        signals: Dict[SemanticRole, float] = {}
        
        if dtype in ("integer", "float", "numeric"):
            signals[SemanticRole.QUANTITY] = 0.3
            signals[SemanticRole.REVENUE] = 0.25
            signals[SemanticRole.COST] = 0.25
            signals[SemanticRole.PRICE] = 0.25
            signals[SemanticRole.PERCENTAGE] = 0.2
        
        if dtype in ("date", "datetime"):
            signals[SemanticRole.DATE] = 0.5
            signals[SemanticRole.DATETIME] = 0.4
        
        if dtype == "string":
            signals[SemanticRole.ENTITY] = 0.2
            signals[SemanticRole.STATUS] = 0.15
            signals[SemanticRole.COUNTRY] = 0.1
        
        return signals
    
    def _distribution_signals(self, series: pd.Series, dtype: str) -> Dict[SemanticRole, float]:
        """Signal scores based on value distribution."""
        signals: Dict[SemanticRole, float] = {}
        non_null = series.dropna()
        
        if len(non_null) == 0:
            return signals
        
        # Numeric analysis
        if dtype in ("integer", "float", "numeric"):
            try:
                values = pd.to_numeric(non_null, errors="coerce").dropna()
                if len(values) > 0:
                    min_v, max_v = values.min(), values.max()
                    range_v = max_v - min_v
                    
                    # Small integers often identity or count
                    if max_v < 1000 and min_v >= 0 and range_v > 0:
                        signals[SemanticRole.QUANTITY] = 0.15
                    
                    # Percentage-like range (0-100)
                    if 0 <= min_v and max_v <= 100:
                        signals[SemanticRole.PERCENTAGE] = 0.2
                    
                    # Large positive values → likely financial
                    if min_v >= 0 and max_v > 1000:
                        signals[SemanticRole.REVENUE] = 0.1
                        signals[SemanticRole.COST] = 0.1
            except (ValueError, TypeError):
                pass
        
        # Date analysis
        if dtype in ("date", "datetime"):
            signals[SemanticRole.DATE] = 0.15
        
        return signals
    
    def _generate_notes(self, col_name: str, dtype: str, null_pct: float, unique_count: int) -> str:
        """Generate human-readable notes about the column."""
        notes = []
        
        if null_pct > 50:
            notes.append(f"High NULL rate ({null_pct:.1f}%)")
        
        if dtype == "string" and unique_count == 1:
            notes.append("Constant value (all rows identical)")
        
        if unique_count == 0:
            notes.append("Empty column")
        
        return "; ".join(notes) if notes else None
