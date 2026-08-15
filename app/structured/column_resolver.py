"""
PHASE 4: Semantic-to-Physical Column Resolver

CRITICAL: This is the ONLY place in the codebase allowed to map semantic roles
to physical column names.

Every component (planner, executor) calls resolve_semantic_column() —
never inlines its own column lookup logic.

If the schema doesn't contain a role, or it's marked AMBIGUOUS_SCHEMA,
returns None (caller must handle gracefully).
"""

from typing import Optional
from app.db.models import StructuredFileSchema
from app.structured.schema_discovery import SemanticRole, ColumnMetadata
from app.utils.logger import logger


def resolve_semantic_column(
    semantic_role: SemanticRole,
    schema: StructuredFileSchema,
) -> Optional[str]:
    """
    Resolve a semantic role to a physical column name in a specific file's schema.
    
    CRITICAL: This is the single source of truth for semantic→physical mapping.
    
    Args:
        semantic_role: The semantic role we're looking for (e.g., SemanticRole.QUANTITY)
        schema: StructuredFileSchema record containing column metadata
    
    Returns:
        Physical column name if found and HIGH confidence (>=0.85)
        None if: not found, ambiguous (<0.85 confidence), or schema inconsistent
    """
    
    if not schema or not schema.columns:
        logger.warning(f"Schema has no columns")
        return None
    
    # Iterate through columns looking for matching semantic role
    for col_dict in schema.columns:
        # Parse column metadata from stored dict
        try:
            col_role_str = col_dict.get("semantic_role", "unknown")
            col_status = col_dict.get("status", "UNMAPPED")
            col_confidence = col_dict.get("confidence", 0.0)
            col_name = col_dict.get("original_name")
            
            # Parse role enum
            try:
                col_role = SemanticRole(col_role_str)
            except ValueError:
                col_role = SemanticRole.UNKNOWN
            
            # Check if this column matches the requested role
            if col_role == semantic_role:
                # Only return if HIGH confidence (>=0.85)
                if col_confidence >= 0.85 and col_status == "MAPPED":
                    logger.debug(
                        f"Resolved {semantic_role.value} → '{col_name}' "
                        f"(confidence: {col_confidence:.2f})"
                    )
                    return col_name
                else:
                    # Low confidence or ambiguous — don't return
                    logger.debug(
                        f"Skipping {col_name} for {semantic_role.value}: "
                        f"status={col_status}, confidence={col_confidence:.2f} (need ≥0.85)"
                    )
                    continue
        
        except Exception as e:
            logger.warning(f"Error processing column metadata: {e}")
            continue
    
    # Not found with high confidence
    logger.debug(f"Could not resolve {semantic_role.value} in schema")
    return None


def resolve_multiple_columns(
    semantic_roles: list,
    schema: StructuredFileSchema,
) -> dict:
    """
    Resolve multiple semantic roles to physical columns.
    
    Args:
        semantic_roles: List of SemanticRole enums to resolve
        schema: StructuredFileSchema
    
    Returns:
        Dict mapping role→column_name for all resolved roles
        Missing roles simply absent from dict (not None values)
    """
    resolved = {}
    
    for role in semantic_roles:
        col_name = resolve_semantic_column(role, schema)
        if col_name is not None:
            resolved[role] = col_name
    
    return resolved


def get_ambiguous_columns(schema: StructuredFileSchema) -> list:
    """
    Get all ambiguous columns in a schema (for UI flagging/resolution).
    
    Args:
        schema: StructuredFileSchema
    
    Returns:
        List of dicts with column name, possible roles, sample values
    """
    ambiguous = []
    
    if not schema or not schema.columns:
        return ambiguous
    
    for col_dict in schema.columns:
        status = col_dict.get("status", "UNMAPPED")
        if status == "AMBIGUOUS_SCHEMA":
            ambiguous.append({
                "original_name": col_dict.get("original_name"),
                "normalized_name": col_dict.get("normalized_name"),
                "data_type": col_dict.get("data_type"),
                "current_role": col_dict.get("semantic_role"),
                "possible_roles": col_dict.get("possible_roles", []),
                "confidence": col_dict.get("confidence"),
                "sample_values": col_dict.get("sample_values", []),
                "notes": col_dict.get("notes"),
            })
    
    return ambiguous
