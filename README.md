# Equity Trend and Valuation Dashboard

A statistical equity analysis dashboard that models ideal stock price trajectories and evaluates broad market valuation using the Buffett Indicator. Built for quantitative finance research, valuation studies, and exploratory analysis.

## Overview

This project provides an interactive Streamlit dashboard that evaluates whether a stock is overvalued, undervalued, or fairly priced relative to an ideal statistical growth trend. It also computes the Buffett Indicator (Total Market Cap divided by GDP) using data from FRED, with an automatic fallback dataset.

## Features

### Stock Trend Modeling
- Log-linear trend (CAGR model)
- Polynomial-smoothed log trend (noise-reduced fair value curve)
- Percent deviation from ideal trajectory
- Adjustable date range
- Interactive Plotly charts

### Buffett Indicator
- Fetches Wilshire 5000 Total Market Cap and GDP from FRED
- Computes Buffett ratio over time
- Compares against historical median
- Provides valuation context (cheap, fair, expensive)

### Streamlit Dashboard
- Real-time inputs (ticker, dates, trend model)
- Two-panel visualization (price chart + Buffett chart)
- Summary statistics and valuation commentary

## Tech Stack

Dashboard: Streamlit, Plotly  
Data: pandas, NumPy  
APIs: Yahoo Finance, FRED  
Modeling: Log-space regression, polynomial smoothing  
Structure: Modular Python package layout



## Running the Project

1. Install dependencies:  pip install -r requirements.txt
2. Run the Streamlit app: streamlit run app/main.py


## Methodology

### Ideal Trend Models

1. Log-linear (CAGR) model  
   - Apply log transform to prices  
   - Fit linear regression over time  
   - Exponentiate fitted line back to price space  
   - Represents long-term exponential growth

2. Smoothed log trend  
   - Log-transform the price  
   - Apply polynomial smoothing  
   - Noise-reduced fair-value curve  

### Deviation Metric

Deviation (%) = (Actual Price - Ideal Price) / Ideal Price * 100

Interpretation:  
Above 20%: likely overvalued  
0% to 20%: slightly overvalued  
0% to -20%: slightly undervalued  
Below -20%: undervalued

### Buffett Indicator

Buffett Ratio = Total Market Cap / GDP

Interpretation:  
Below 70%: undervalued  
Around 100%: fairly valued  
Above 120%: overvalued  
Above 150%: highly overvalued

## License

MIT License

## Acknowledgements

- Yahoo Finance  
- FRED (Federal Reserve Economic Data)  
- Streamlit and Plotly documentation



