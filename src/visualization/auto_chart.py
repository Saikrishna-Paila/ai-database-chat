"""
Automatic Chart Generation based on Query Results
"""

from typing import Dict, Any, List, Optional
import pandas as pd

# Conditional imports for visualization
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    px = None
    go = None


class AutoChartGenerator:
    """Automatically generates appropriate charts based on data characteristics"""

    def __init__(self):
        self.supported_chart_types = [
            "bar", "line", "pie", "scatter", "histogram", "table"
        ]

    def analyze_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze DataFrame to determine best visualization"""
        if df.empty:
            return {"chart_type": "table", "reason": "Empty dataset"}

        analysis = {
            "row_count": len(df),
            "column_count": len(df.columns),
            "numeric_columns": df.select_dtypes(include=['number']).columns.tolist(),
            "categorical_columns": df.select_dtypes(include=['object', 'category']).columns.tolist(),
            "datetime_columns": df.select_dtypes(include=['datetime64']).columns.tolist()
        }

        # Determine chart type based on data characteristics
        chart_type = self._suggest_chart_type(analysis)
        analysis["suggested_chart_type"] = chart_type

        return analysis

    def _suggest_chart_type(self, analysis: Dict[str, Any]) -> str:
        """Suggest the best chart type based on data analysis"""
        num_cols = len(analysis["numeric_columns"])
        cat_cols = len(analysis["categorical_columns"])
        date_cols = len(analysis["datetime_columns"])
        row_count = analysis["row_count"]

        # Time series data
        if date_cols >= 1 and num_cols >= 1:
            return "line"

        # Categorical with numeric (good for bar charts)
        if cat_cols >= 1 and num_cols >= 1:
            if row_count <= 10:
                return "pie"
            return "bar"

        # Two numeric columns (scatter plot)
        if num_cols >= 2:
            return "scatter"

        # Single numeric column (histogram)
        if num_cols == 1:
            return "histogram"

        # Default to table
        return "table"

    def generate_chart(
        self,
        df: pd.DataFrame,
        chart_type: Optional[str] = None,
        title: str = "Query Results",
        x_column: Optional[str] = None,
        y_column: Optional[str] = None
    ) -> Optional[Any]:
        """Generate a chart from DataFrame"""
        if not PLOTLY_AVAILABLE:
            return None

        if df.empty:
            return None

        # Auto-detect chart type if not specified
        if chart_type is None:
            analysis = self.analyze_data(df)
            chart_type = analysis["suggested_chart_type"]

        # Auto-detect columns if not specified
        if x_column is None or y_column is None:
            x_column, y_column = self._auto_select_columns(df, chart_type)

        # Generate chart based on type
        chart_generators = {
            "bar": self._create_bar_chart,
            "line": self._create_line_chart,
            "pie": self._create_pie_chart,
            "scatter": self._create_scatter_chart,
            "histogram": self._create_histogram,
            "table": self._create_table
        }

        generator = chart_generators.get(chart_type, self._create_table)
        return generator(df, title, x_column, y_column)

    def _auto_select_columns(
        self,
        df: pd.DataFrame,
        chart_type: str
    ) -> tuple:
        """Auto-select appropriate columns for visualization"""
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()

        x_col = None
        y_col = None

        if chart_type in ["bar", "pie"]:
            x_col = categorical_cols[0] if categorical_cols else df.columns[0]
            y_col = numeric_cols[0] if numeric_cols else df.columns[1] if len(df.columns) > 1 else df.columns[0]

        elif chart_type == "line":
            x_col = datetime_cols[0] if datetime_cols else (categorical_cols[0] if categorical_cols else df.columns[0])
            y_col = numeric_cols[0] if numeric_cols else df.columns[1] if len(df.columns) > 1 else df.columns[0]

        elif chart_type == "scatter":
            if len(numeric_cols) >= 2:
                x_col = numeric_cols[0]
                y_col = numeric_cols[1]
            else:
                x_col = df.columns[0]
                y_col = df.columns[1] if len(df.columns) > 1 else df.columns[0]

        elif chart_type == "histogram":
            x_col = numeric_cols[0] if numeric_cols else df.columns[0]
            y_col = None

        return x_col, y_col

    def _create_bar_chart(
        self,
        df: pd.DataFrame,
        title: str,
        x_col: str,
        y_col: str
    ):
        """Create a bar chart"""
        fig = px.bar(df, x=x_col, y=y_col, title=title)
        fig.update_layout(
            xaxis_title=x_col,
            yaxis_title=y_col,
            template="plotly_white"
        )
        return fig

    def _create_line_chart(
        self,
        df: pd.DataFrame,
        title: str,
        x_col: str,
        y_col: str
    ):
        """Create a line chart"""
        fig = px.line(df, x=x_col, y=y_col, title=title)
        fig.update_layout(
            xaxis_title=x_col,
            yaxis_title=y_col,
            template="plotly_white"
        )
        return fig

    def _create_pie_chart(
        self,
        df: pd.DataFrame,
        title: str,
        x_col: str,
        y_col: str
    ):
        """Create a pie chart"""
        fig = px.pie(df, names=x_col, values=y_col, title=title)
        fig.update_layout(template="plotly_white")
        return fig

    def _create_scatter_chart(
        self,
        df: pd.DataFrame,
        title: str,
        x_col: str,
        y_col: str
    ):
        """Create a scatter plot"""
        fig = px.scatter(df, x=x_col, y=y_col, title=title)
        fig.update_layout(
            xaxis_title=x_col,
            yaxis_title=y_col,
            template="plotly_white"
        )
        return fig

    def _create_histogram(
        self,
        df: pd.DataFrame,
        title: str,
        x_col: str,
        y_col: str
    ):
        """Create a histogram"""
        fig = px.histogram(df, x=x_col, title=title)
        fig.update_layout(
            xaxis_title=x_col,
            yaxis_title="Count",
            template="plotly_white"
        )
        return fig

    def _create_table(
        self,
        df: pd.DataFrame,
        title: str,
        x_col: str,
        y_col: str
    ):
        """Create a table visualization"""
        fig = go.Figure(data=[go.Table(
            header=dict(
                values=list(df.columns),
                fill_color='paleturquoise',
                align='left'
            ),
            cells=dict(
                values=[df[col] for col in df.columns],
                fill_color='lavender',
                align='left'
            )
        )])
        fig.update_layout(title=title)
        return fig

    def get_chart_recommendation(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get chart recommendation with explanation"""
        analysis = self.analyze_data(df)

        explanations = {
            "bar": "Bar chart recommended for comparing categorical values",
            "line": "Line chart recommended for showing trends over time",
            "pie": "Pie chart recommended for showing proportions (small dataset)",
            "scatter": "Scatter plot recommended for showing correlation between numeric variables",
            "histogram": "Histogram recommended for showing distribution of numeric data",
            "table": "Table view recommended for detailed data inspection"
        }

        return {
            "recommended_chart": analysis["suggested_chart_type"],
            "explanation": explanations.get(analysis["suggested_chart_type"], ""),
            "data_analysis": analysis,
            "available_charts": self.supported_chart_types
        }
