#!/usr/bin/env python3
"""
Test to verify GROUP BY removal for "total" queries.
"""

from app.structured.sql_generator import LLMSQLGenerator
import re

def test_group_by_removal():
    """Test that GROUP BY is removed from "total" queries."""
    
    print("=" * 80)
    print("TEST: GROUP BY Removal for Total Queries")
    print("=" * 80)
    
    generator = LLMSQLGenerator()
    
    test_cases = [
        (
            "SELECT Date, SUM(Profit) FROM table GROUP BY Date ORDER BY SUM(Profit) DESC",
            "What's the total profit?",
            "Should remove GROUP BY and ORDER BY"
        ),
        (
            "SELECT SUM(Revenue) FROM table",
            "Total revenue",
            "Already correct - no GROUP BY"
        ),
        (
            "SELECT Date, SUM(Cost) as daily_cost FROM kb_table GROUP BY Date ORDER BY daily_cost DESC LIMIT 10",
            "total cost for all days",
            "Should remove GROUP BY, ORDER BY, LIMIT"
        ),
    ]
    
    all_pass = True
    
    for sql, query, description in test_cases:
        print(f"\n[TEST] {description}")
        print(f"Query: {query}")
        print(f"Input SQL:\n  {sql}")
        
        try:
            fixed_sql = generator._fix_group_by_for_total_queries(sql, query)
            
            # Check if GROUP BY was removed
            has_group_by = "GROUP BY" in fixed_sql.upper()
            asked_for_total = ("total" in query.lower() or "sum" in query.lower()) and "which" not in query.lower()
            
            if asked_for_total:
                passed = not has_group_by
                status = "[PASS]" if passed else "[FAIL]"
                print(f"{status} - GROUP BY removed: {not has_group_by}")
                if has_group_by:
                    all_pass = False
            else:
                status = "[SKIP]" if "which" in query.lower() else "[PASS]"
                print(f"{status} - Not a 'total' query")
            
            print(f"Output SQL:\n  {fixed_sql}")
        
        except Exception as e:
            print(f"[ERROR]: {e}")
            all_pass = False
    
    print("\n" + "=" * 80)
    if all_pass:
        print("[SUCCESS] All safeguards working!")
    else:
        print("[FAILED] Some safeguards not working")
    print("=" * 80)
    
    return all_pass


if __name__ == "__main__":
    try:
        success = test_group_by_removal()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n[FATAL ERROR]: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
