"""
Utility Helper Functions
"""

import json
import re
from typing import Dict, Any, List, Optional
import pandas as pd


def format_results(results: Dict[str, Any], max_rows: int = 20) -> str:
    """Format query results for display"""
    if not results.get("success"):
        return f"Error: {results.get('error', 'Unknown error')}"

    data = results.get("data", [])
    row_count = results.get("row_count", 0)

    if not data:
        return "No results found."

    # Create DataFrame for formatting
    df = pd.DataFrame(data[:max_rows])

    output = []
    output.append(f"Results: {row_count} rows")

    if row_count > max_rows:
        output.append(f"(showing first {max_rows} rows)")

    output.append("")
    output.append(df.to_string(index=False))

    return "\n".join(output)


def format_sql(sql: str) -> str:
    """Format SQL query for display"""
    # Basic SQL formatting
    keywords = [
        'SELECT', 'FROM', 'WHERE', 'JOIN', 'LEFT JOIN', 'RIGHT JOIN',
        'INNER JOIN', 'OUTER JOIN', 'ON', 'AND', 'OR', 'ORDER BY',
        'GROUP BY', 'HAVING', 'LIMIT', 'OFFSET', 'INSERT', 'UPDATE',
        'DELETE', 'CREATE', 'ALTER', 'DROP', 'UNION', 'EXCEPT', 'INTERSECT'
    ]

    formatted = sql.strip()

    # Add newlines before major keywords
    for keyword in keywords:
        pattern = r'\b' + keyword + r'\b'
        formatted = re.sub(pattern, '\n' + keyword, formatted, flags=re.IGNORECASE)

    # Clean up multiple newlines
    formatted = re.sub(r'\n+', '\n', formatted)

    return formatted.strip()


def format_mongo_query(query: Dict[str, Any]) -> str:
    """Format MongoDB query for display"""
    return json.dumps(query, indent=2, default=str)


def validate_sql_safety(sql: str, blocked_keywords: List[str]) -> Dict[str, Any]:
    """Validate SQL query for safety"""
    sql_upper = sql.upper()

    for keyword in blocked_keywords:
        if keyword.upper() in sql_upper:
            return {
                "safe": False,
                "reason": f"Query contains blocked keyword: {keyword}"
            }

    # Check for multiple statements
    if sql.count(';') > 1:
        return {
            "safe": False,
            "reason": "Multiple SQL statements not allowed"
        }

    return {"safe": True, "reason": None}


def validate_mongo_safety(query: Dict[str, Any]) -> Dict[str, Any]:
    """Validate MongoDB query for safety"""
    # Check for dangerous operators
    dangerous_operators = ['$where', '$function']

    def check_dict(d: Dict) -> Optional[str]:
        for key, value in d.items():
            if key in dangerous_operators:
                return f"Query contains dangerous operator: {key}"
            if isinstance(value, dict):
                result = check_dict(value)
                if result:
                    return result
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        result = check_dict(item)
                        if result:
                            return result
        return None

    reason = check_dict(query)
    if reason:
        return {"safe": False, "reason": reason}

    return {"safe": True, "reason": None}


def extract_table_references(sql: str) -> List[str]:
    """Extract table names referenced in a SQL query"""
    # Simple regex-based extraction
    from_pattern = r'FROM\s+["\']?(\w+)["\']?'
    join_pattern = r'JOIN\s+["\']?(\w+)["\']?'

    tables = []
    tables.extend(re.findall(from_pattern, sql, re.IGNORECASE))
    tables.extend(re.findall(join_pattern, sql, re.IGNORECASE))

    return list(set(tables))


def truncate_text(text: str, max_length: int = 500) -> str:
    """Truncate text to max length with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def dataframe_to_dict_list(df: pd.DataFrame) -> List[Dict]:
    """Convert DataFrame to list of dictionaries"""
    return df.to_dict(orient='records')


def estimate_query_complexity(sql: str) -> str:
    """Estimate query complexity based on keywords"""
    sql_upper = sql.upper()

    complex_keywords = ['JOIN', 'SUBQUERY', 'WITH', 'UNION', 'HAVING']
    medium_keywords = ['GROUP BY', 'ORDER BY', 'DISTINCT']

    complex_count = sum(1 for kw in complex_keywords if kw in sql_upper)
    medium_count = sum(1 for kw in medium_keywords if kw in sql_upper)

    if complex_count >= 2 or 'SUBQUERY' in sql_upper:
        return "high"
    elif complex_count >= 1 or medium_count >= 2:
        return "medium"
    else:
        return "low"
