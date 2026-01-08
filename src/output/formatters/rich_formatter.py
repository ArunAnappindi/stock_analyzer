"""
Rich console formatter for beautiful terminal output.
"""

from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box
from src.models import AnalysisResult, Signal, RiskLevel


class RichFormatter:
    """Formatter that produces rich console output."""

    def __init__(self):
        """Initialize the rich formatter."""
        self.console = Console()

    def format(self, result: AnalysisResult) -> None:
        """
        Format and display the analysis result using rich console.

        Args:
            result: AnalysisResult to format
        """
        self.console.print()

        # Header
        self._print_header(result)

        # Stock Overview
        self._print_stock_overview(result)

        # Technical Analysis
        self._print_technical_analysis(result)

        # Volume Analysis
        self._print_volume_analysis(result)

        # Sentiment Analysis
        self._print_sentiment_analysis(result)

        # Trade Recommendation (most important!)
        self._print_trade_recommendation(result)

        # Warnings if any
        if result.warnings:
            self._print_warnings(result.warnings)

        # Risk Disclaimer
        self._print_disclaimer(result.disclaimer)

        self.console.print()

    def _print_header(self, result: AnalysisResult):
        """Print header with ticker and timestamp."""
        title = Text(f"📊 STOCK ANALYSIS REPORT: {result.ticker}", style="bold cyan")
        subtitle = Text(
            f"Generated at: {result.timestamp} | Data Quality: {result.data_quality}",
            style="dim"
        )

        header = Text.assemble(title, "\n", subtitle)
        self.console.print(Panel(header, box=box.DOUBLE, border_style="cyan"))

    def _print_stock_overview(self, result: AnalysisResult):
        """Print stock overview section."""
        table = Table(title="Stock Overview", box=box.ROUNDED, title_style="bold yellow")

        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="white")

        table.add_row("Current Price", f"${result.current_price:.2f}")

        price_change = result.current_price - (result.current_price / 1.01)  # Approximate
        change_style = "green" if price_change >= 0 else "red"

        table.add_row(
            "Trend",
            Text(result.technical_analysis.trend.value.upper(), style=change_style)
        )

        table.add_row(
            "Volume Status",
            f"{result.volume_analysis.relative_volume:.1f}x average"
        )

        self.console.print(table)
        self.console.print()

    def _print_technical_analysis(self, result: AnalysisResult):
        """Print technical analysis section."""
        tech = result.technical_analysis
        indicators = tech.indicators

        table = Table(
            title="📈 Technical Analysis",
            box=box.ROUNDED,
            title_style="bold green"
        )

        table.add_column("Indicator", style="cyan")
        table.add_column("Value", style="white")
        table.add_column("Interpretation", style="yellow")

        # EMAs
        if indicators.ema_20:
            table.add_row("EMA 20", f"${indicators.ema_20:.2f}", "-")
        if indicators.ema_50:
            table.add_row("EMA 50", f"${indicators.ema_50:.2f}", "-")

        # VWAP
        if indicators.vwap:
            vwap_status = "Above ✓" if tech.price_above_vwap else "Below ✗"
            table.add_row("VWAP", f"${indicators.vwap:.2f}", vwap_status)

        # RSI
        if indicators.rsi:
            table.add_row("RSI (14)", f"{indicators.rsi:.1f}", tech.rsi_interpretation.capitalize())

        # MACD
        if indicators.macd:
            table.add_row(
                "MACD",
                f"{indicators.macd:.2f}",
                tech.macd_interpretation.capitalize()
            )

        # Support/Resistance
        if indicators.support_level:
            table.add_row("Support", f"${indicators.support_level:.2f}", "-")
        if indicators.resistance_level:
            table.add_row("Resistance", f"${indicators.resistance_level:.2f}", "-")

        table.add_row("", "", "")  # Separator
        table.add_row(
            "Overall Signal",
            tech.overall_signal.upper(),
            f"Confidence: {tech.confidence}%"
        )

        self.console.print(table)

        # Summary
        self.console.print(f"[dim]{tech.summary}[/dim]")
        self.console.print()

    def _print_volume_analysis(self, result: AnalysisResult):
        """Print volume analysis section."""
        vol = result.volume_analysis

        table = Table(
            title="📊 Volume Analysis",
            box=box.ROUNDED,
            title_style="bold blue"
        )

        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="white")

        table.add_row("Current Volume", f"{vol.current_volume:,}")
        table.add_row("Average Volume", f"{vol.avg_volume:,.0f}")
        table.add_row("Relative Volume", f"{vol.relative_volume:.2f}x")

        spike_status = "YES ⚠️" if vol.volume_spike_detected else "No"
        table.add_row("Volume Spike", spike_status)

        conf_status = "YES ✓" if vol.price_volume_confirmation else "No"
        table.add_row("Price-Volume Confirmation", conf_status)

        table.add_row(
            "Interpretation",
            vol.interpretation.upper()
        )

        self.console.print(table)
        self.console.print(f"[dim]{vol.summary}[/dim]")
        self.console.print()

    def _print_sentiment_analysis(self, result: AnalysisResult):
        """Print sentiment analysis section."""
        sent = result.sentiment_analysis

        table = Table(
            title="💭 Sentiment Analysis",
            box=box.ROUNDED,
            title_style="bold magenta"
        )

        table.add_column("Source", style="cyan")
        table.add_column("Sentiment", style="white")
        table.add_column("Score", style="yellow")

        # News sentiment
        table.add_row(
            "News",
            sent.news_sentiment.value.replace("_", " ").title(),
            f"{sent.news_score:+.2f}"
        )

        # Overall sentiment
        table.add_row("", "", "")  # Separator
        table.add_row(
            "Overall",
            sent.overall_sentiment.value.replace("_", " ").upper(),
            f"Confidence: {sent.confidence}%"
        )

        self.console.print(table)

        # Catalysts
        if sent.major_catalysts:
            catalyst_text = Text("Catalysts Detected: ", style="bold")
            catalyst_text.append(", ".join(sent.major_catalysts), style="yellow")
            self.console.print(catalyst_text)

        self.console.print(f"[dim]{sent.summary}[/dim]")
        self.console.print()

    def _print_trade_recommendation(self, result: AnalysisResult):
        """Print the trade recommendation - the most important section."""
        rec = result.trade_recommendation

        # Determine style based on signal
        if rec.signal == Signal.STRONG_BUY:
            title_style = "bold green"
            border_style = "green"
        elif rec.signal == Signal.MODERATE_BUY:
            title_style = "bold yellow"
            border_style = "yellow"
        elif rec.signal == Signal.WEAK_BUY:
            title_style = "bold cyan"
            border_style = "cyan"
        else:
            title_style = "bold white"
            border_style = "white"

        table = Table(
            title="🎯 TRADE RECOMMENDATION",
            box=box.DOUBLE,
            title_style=title_style,
            border_style=border_style
        )

        table.add_column("Parameter", style="cyan bold", width=20)
        table.add_column("Value", style="white bold", width=40)

        # Signal
        signal_text = rec.signal.value.replace("_", " ").upper()
        table.add_row("Trade Bias", Text(signal_text, style=title_style))

        # Confidence
        table.add_row("Confidence Score", f"{rec.confidence}%")

        # If BUY signal, show price levels
        if rec.signal in [Signal.STRONG_BUY, Signal.MODERATE_BUY, Signal.WEAK_BUY]:
            if rec.entry_price:
                table.add_row("", "")  # Separator
                table.add_row("Entry Price", f"${rec.entry_price:.2f}")
                table.add_row("Target Price", f"${rec.target_price:.2f}")
                table.add_row("Stop Loss", f"${rec.stop_loss:.2f}")

                if rec.risk_reward_ratio:
                    table.add_row("Risk:Reward Ratio", f"1:{rec.risk_reward_ratio:.2f}")

                table.add_row("Max Quantity", f"{rec.max_quantity} shares")
                table.add_row("Risk Level", rec.risk_level.value.upper())

                if rec.risk_amount:
                    table.add_row("Risk Amount", f"${rec.risk_amount:.2f}")
                if rec.potential_profit:
                    table.add_row("Potential Profit", f"${rec.potential_profit:.2f}")

                table.add_row("Holding Time", rec.estimated_hold_time)

        self.console.print(table)

        # Reasoning
        self.console.print(Panel(
            rec.reasoning,
            title="[bold]Reasoning[/bold]",
            border_style="dim"
        ))

        # Key Factors
        if rec.key_factors:
            factors_text = Text("Key Factors: ", style="bold")
            factors_text.append(" • ".join(rec.key_factors), style="cyan")
            self.console.print(factors_text)

        self.console.print()

    def _print_warnings(self, warnings: list[str]):
        """Print warnings if any."""
        warning_text = Text("\n⚠️  WARNINGS:\n", style="bold yellow")
        for warning in warnings:
            warning_text.append(f"  • {warning}\n", style="yellow")

        self.console.print(Panel(warning_text, border_style="yellow"))

    def _print_disclaimer(self, disclaimer: str):
        """Print risk disclaimer."""
        self.console.print(Panel(
            disclaimer,
            title="[bold red]⚠️  RISK DISCLAIMER[/bold red]",
            border_style="red",
            box=box.DOUBLE
        ))
