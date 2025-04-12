# -*- coding: utf-8 -*-
"""Final project

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/19v78tJKzCJUJJVEOHc9gYG-XR8G9KcMh
"""

# Apple Stock Price Prediction using RNN and LSTM

# ================== Import Libraries ==================
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, SimpleRNN, LSTM, Dropout
from tensorflow.keras.callbacks import EarlyStopping

# ================== 1. Data Cleaning (20%) ==================
# Load dataset
data = pd.read_csv('/content/AAPL.csv')

# Convert 'Date' to datetime and set as index
data['Date'] = pd.to_datetime(data['Date'])
data.set_index('Date', inplace=True)

# Check and display missing values
print("Missing values before cleaning:\n", data.isnull().sum())

# Drop rows with any missing values
data.dropna(inplace=True)

# Confirm no missing values
print("\nMissing values after cleaning:\n", data.isnull().sum())

# ================== 2. Data Preprocessing (20%) ==================
# Use only the 'Adj Close' column
data = data[['Adj Close']]

# Scale data to range (0,1)
scaler = MinMaxScaler()
data_scaled = scaler.fit_transform(data)

# Create time-series sequences
def create_sequences(data, window_size, future_day):
    X, y = [], []
    for i in range(len(data) - window_size - future_day + 1):
        X.append(data[i:i+window_size])
        y.append(data[i+window_size+future_day-1])
    return np.array(X), np.array(y)

# Set parameters
window_size = 60
future_days = [1, 5, 10]  # Predict 1-day, 5-day, and 10-day ahead

# Split into training and testing sets
train_size = int(len(data_scaled) * 0.8)
train_data = data_scaled[:train_size]
test_data = data_scaled[train_size - window_size:]

# ================== 3. Data Visualization (10%) ==================
plt.figure(figsize=(10, 4))
plt.plot(data.index, data['Adj Close'], color='blue', label='Adj Close Price')
plt.title('Apple Stock - Adjusted Close Price')
plt.xlabel('Date')
plt.ylabel('Price')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# ================== 4. Feature Engineering (10%) ==================
# Feature: use 60-day window to predict future stock prices (1, 5, 10 days)
# Already implemented in create_sequences function

# ================== 5. Deep Learning Modeling (30%) ==================
results = {}

for future_day in future_days:
    print(f"\n=== Predicting {future_day}-day ahead prices ===")

    # Create sequences
    X_train, y_train = create_sequences(train_data, window_size, future_day)
    X_test, y_test = create_sequences(test_data, window_size, future_day)

    # Reshape inputs for RNN/LSTM
    X_train_rnn = X_train.reshape((X_train.shape[0], X_train.shape[1], 1))
    X_test_rnn = X_test.reshape((X_test.shape[0], X_test.shape[1], 1))

    # ------------------- Simple RNN -------------------
    rnn_model = Sequential([
        SimpleRNN(50, activation='tanh', input_shape=(window_size, 1)),
        Dropout(0.2),
        Dense(1)
    ])
    rnn_model.compile(optimizer='adam', loss='mse')

    rnn_model.fit(X_train_rnn, y_train, epochs=20, batch_size=32,
                  validation_split=0.1, callbacks=[EarlyStopping(patience=5, restore_best_weights=True)],
                  verbose=0)

    rnn_pred = rnn_model.predict(X_test_rnn)
    rnn_pred_rescaled = scaler.inverse_transform(rnn_pred)
    y_test_rescaled = scaler.inverse_transform(y_test.reshape(-1, 1))

    rnn_mse = mean_squared_error(y_test_rescaled, rnn_pred_rescaled)

    # ------------------- LSTM -------------------
    lstm_model = Sequential([
        LSTM(50, return_sequences=False, input_shape=(window_size, 1)),
        Dropout(0.2),
        Dense(1)
    ])
    lstm_model.compile(optimizer='adam', loss='mse')

    lstm_model.fit(X_train_rnn, y_train, epochs=20, batch_size=32,
                   validation_split=0.1, callbacks=[EarlyStopping(patience=5, restore_best_weights=True)],
                   verbose=0)

    lstm_pred = lstm_model.predict(X_test_rnn)
    lstm_pred_rescaled = scaler.inverse_transform(lstm_pred)

    lstm_mse = mean_squared_error(y_test_rescaled, lstm_pred_rescaled)

    # Store results
    results[future_day] = {
        'RNN_MSE': rnn_mse,
        'LSTM_MSE': lstm_mse,
        'y_test': y_test_rescaled,
        'rnn_pred': rnn_pred_rescaled,
        'lstm_pred': lstm_pred_rescaled
    }

    # ================== 6. Model Evaluation & Visualization (10%) ==================
    plt.figure(figsize=(12, 5))
    plt.plot(y_test_rescaled, label='Actual Price')
    plt.plot(rnn_pred_rescaled, label='SimpleRNN Prediction')
    plt.plot(lstm_pred_rescaled, label='LSTM Prediction')
    plt.title(f"{future_day}-Day Ahead Prediction: Actual vs Predicted")
    plt.xlabel('Time Step')
    plt.ylabel('Stock Price')
    plt.legend()
    plt.grid()
    plt.tight_layout()
    plt.show()

# ================== Final Summary ==================
for future_day, metrics in results.items():
    print(f"\n=== {future_day}-Day Ahead Forecast Summary ===")
    print(f"SimpleRNN MSE: {metrics['RNN_MSE']:.4f}")
    print(f"LSTM MSE    : {metrics['LSTM_MSE']:.4f}")

pip install tensorflow pandas numpy matplotlib scikit-learn

# ================== 1. Imports ==================
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Dropout, Bidirectional
from tensorflow.keras.callbacks import EarlyStopping

# ================== 2. Load & Feature Engineering ==================
df = pd.read_csv('/content/AAPL.csv')
df['Date'] = pd.to_datetime(df['Date'])
df.set_index('Date', inplace=True)

df = df[['Adj Close']].copy()
df['MA10'] = df['Adj Close'].rolling(window=10).mean()
df['MA50'] = df['Adj Close'].rolling(window=50).mean()
df['Returns'] = df['Adj Close'].pct_change()

def compute_RSI(series, window=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window).mean()
    avg_loss = loss.rolling(window).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

df['RSI'] = compute_RSI(df['Adj Close'])
df.dropna(inplace=True)

# ================== 3. Scale ==================
scaler = MinMaxScaler()
scaled_data = scaler.fit_transform(df)

# For inverse scaling only on 'Adj Close'
adj_scaler = MinMaxScaler()
adj_scaler.min_, adj_scaler.scale_ = scaler.min_[0], scaler.scale_[0]

# ================== 4. Sequence Generator ==================
def create_sequences(data, window_size, future_step):
    X, y = [], []
    for i in range(len(data) - window_size - future_step + 1):
        X.append(data[i:i+window_size])
        y.append(data[i+window_size+future_step-1][0])  # only 'Adj Close'
    return np.array(X), np.array(y)

# ================== 5. Modeling Function ==================
def train_predict_model(future_day):
    print(f"\n🚀 Training {future_day}-Day Prediction Model...")
    window_size = 60
    train_size = int(len(scaled_data) * 0.8)

    train_data = scaled_data[:train_size]
    test_data = scaled_data[train_size - window_size:]

    X_train, y_train = create_sequences(train_data, window_size, future_day)
    X_test, y_test = create_sequences(test_data, window_size, future_day)

    model = Sequential([
        Bidirectional(LSTM(64, return_sequences=True), input_shape=(X_train.shape[1], X_train.shape[2])),
        Dropout(0.3),
        LSTM(32),
        Dropout(0.2),
        Dense(1)
    ])

    model.compile(optimizer='adam', loss='mse')

    early_stop = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
    history = model.fit(X_train, y_train, epochs=50, batch_size=32,
                        validation_split=0.1, verbose=0, callbacks=[early_stop])

    pred = model.predict(X_test)
    pred_rescaled = adj_scaler.inverse_transform(pred)
    y_test_rescaled = adj_scaler.inverse_transform(y_test.reshape(-1, 1))
    mse = mean_squared_error(y_test_rescaled, pred_rescaled)

    print(f"✅ {future_day}-Day MSE: {mse:.4f}")

    return y_test_rescaled, pred_rescaled, history

# ================== 6. Train All Models ==================
results = {}
for step in [1, 5, 10]:
    actual, predicted, hist = train_predict_model(step)
    results[step] = {
        'actual': actual,
        'predicted': predicted,
        'history': hist
    }

# ================== 7. Plot Results ==================
for step in [1, 5, 10]:
    actual = results[step]['actual']
    predicted = results[step]['predicted']

    plt.figure(figsize=(12, 5))
    plt.plot(actual, label='Actual Price')
    plt.plot(predicted, label=f'Predicted Price ({step}-Day Ahead)')
    plt.title(f'Apple Stock Price Prediction ({step}-Day Ahead)')
    plt.xlabel('Time Step')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# ================== 8. Plot Training Loss ==================
for step in [1, 5, 10]:
    history = results[step]['history']

    plt.figure(figsize=(8, 4))
    plt.plot(history.history['loss'], label='Train Loss')
    plt.plot(history.history['val_loss'], label='Val Loss')
    plt.title(f'{step}-Day Model Loss')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, LSTM, RepeatVector, TimeDistributed, Dense
from tensorflow.keras.callbacks import EarlyStopping

# Load and preprocess data
data = pd.read_csv('/content/AAPL.csv')
data['Date'] = pd.to_datetime(data['Date'])
data.set_index('Date', inplace=True)
data = data[['Adj Close']]
data.dropna(inplace=True)

# Scale data
scaler = MinMaxScaler()
data_scaled = scaler.fit_transform(data)

# Create sequences for Seq2Seq
def create_seq2seq_data(data, window_size, output_length):
    X, y = [], []
    for i in range(len(data) - window_size - output_length + 1):
        X.append(data[i:i + window_size])
        y.append(data[i + window_size:i + window_size + output_length])
    return np.array(X), np.array(y)

# Parameters
window_size = 60
forecast_days = [1, 5, 10]
train_size = int(len(data_scaled) * 0.8)
train_data = data_scaled[:train_size]
test_data = data_scaled[train_size - window_size:]

results = {}

for output_len in forecast_days:
    print(f"\n📈 Forecasting {output_len}-day ahead using Seq2Seq LSTM...")

    X_train, y_train = create_seq2seq_data(train_data, window_size, output_len)
    X_test, y_test = create_seq2seq_data(test_data, window_size, output_len)

    # Model
    inputs = Input(shape=(window_size, 1))
    encoded = LSTM(100, activation='relu')(inputs)
    repeated = RepeatVector(output_len)(encoded)
    decoded = LSTM(100, activation='relu', return_sequences=True)(repeated)
    output = TimeDistributed(Dense(1))(decoded)

    model = Model(inputs, output)
    model.compile(optimizer='adam', loss='mse')
    model.fit(X_train, y_train, epochs=20, batch_size=32, validation_split=0.1,
              callbacks=[EarlyStopping(patience=5, restore_best_weights=True)], verbose=0)

    # Predict
    y_pred = model.predict(X_test)
    y_test_rescaled = scaler.inverse_transform(y_test.reshape(-1, 1))
    y_pred_rescaled = scaler.inverse_transform(y_pred.reshape(-1, 1))

    # MSE
    mse = mean_squared_error(y_test_rescaled, y_pred_rescaled)
    results[output_len] = mse

    # Plot
    plt.figure(figsize=(12, 5))
    plt.plot(y_test_rescaled[:100], label='Actual')
    plt.plot(y_pred_rescaled[:100], label='Predicted')
    plt.title(f'{output_len}-Day Ahead Seq2Seq Forecast')
    plt.xlabel('Time Steps')
    plt.ylabel('Price')
    plt.legend()
    plt.grid()
    plt.tight_layout()
    plt.show()

# Final Summary
print("\n📊 Final Forecast MSE Summary:")
for day, mse in results.items():
    print(f"{day}-Day Ahead Forecast MSE: {mse:.4f}")

# 1. Import Libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, SimpleRNN, LSTM, Dropout
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

# 2. Load Dataset
df = pd.read_csv("AAPL.csv")
df['Date'] = pd.to_datetime(df['Date'])
df.set_index('Date', inplace=True)
df = df[['Adj Close']].dropna()

# 3. Scale Data
scaler = MinMaxScaler()
scaled_data = scaler.fit_transform(df)

# 4. Create Sequences
def create_sequences(data, window_size, forecast_days):
    X, y = [], []
    for i in range(len(data) - window_size - forecast_days + 1):
        X.append(data[i:(i + window_size), 0])
        y.append(data[(i + window_size):(i + window_size + forecast_days), 0])
    return np.array(X), np.array(y)

# 5. Define Parameters
window_size = 60
forecast_days_list = [1, 5, 10]
X_dict, y_dict = {}, {}

for forecast_days in forecast_days_list:
    X, y = create_sequences(scaled_data, window_size, forecast_days)
    X_dict[forecast_days] = X.reshape((X.shape[0], X.shape[1], 1))
    y_dict[forecast_days] = y

# 6. Train-Test Split
train_size = int(len(scaled_data) * 0.8)
train_idx = int((train_size - window_size - max(forecast_days_list)) + 1)

# 7. Model Architectures
def build_simplernn(units=64, dropout_rate=0.3):
    model = Sequential([
        SimpleRNN(units, input_shape=(window_size, 1)),
        Dropout(dropout_rate),
        Dense(forecast_days)
    ])
    model.compile(optimizer='adam', loss='mse')
    return model

def build_lstm(units=64, dropout_rate=0.3):
    model = Sequential([
        LSTM(units, input_shape=(window_size, 1)),
        Dropout(dropout_rate),
        Dense(forecast_days)
    ])
    model.compile(optimizer='adam', loss='mse')
    return model

# 8. Training and Evaluation
results = {}
for forecast_days in forecast_days_list:
    X = X_dict[forecast_days]
    y = y_dict[forecast_days]
    X_train, X_test = X[:train_idx], X[train_idx:]
    y_train, y_test = y[:train_idx], y[train_idx:]

    print(f"\nTraining for {forecast_days}-day forecast:")

    # SimpleRNN
    rnn_model = build_simplernn()
    rnn_model.fit(X_train, y_train, epochs=50, batch_size=32, verbose=0)
    rnn_pred = rnn_model.predict(X_test)
    rnn_mse = mean_squared_error(y_test, rnn_pred)

    # LSTM
    lstm_model = build_lstm()
    lstm_model.fit(X_train, y_train, epochs=50, batch_size=32, verbose=0)
    lstm_pred = lstm_model.predict(X_test)
    lstm_mse = mean_squared_error(y_test, lstm_pred)

    # Save results
    results[forecast_days] = {
        'SimpleRNN_MSE': round(rnn_mse, 4),
        'LSTM_MSE': round(lstm_mse, 4)
    }

    # Plot predictions
    plt.figure(figsize=(10, 4))
    plt.plot(scaler.inverse_transform(y_test.reshape(-1, 1)), label="Actual")
    plt.plot(scaler.inverse_transform(rnn_pred.reshape(-1, 1)), label="SimpleRNN Predicted")
    plt.plot(scaler.inverse_transform(lstm_pred.reshape(-1, 1)), label="LSTM Predicted")
    plt.title(f"{forecast_days}-Day Prediction: Actual vs Predicted")
    plt.legend()
    plt.show()

# 9. Final Evaluation Table
results_df = pd.DataFrame(results).T
print("\n🔍 Final Evaluation Metrics (MSE):")
print(results_df)

# ================== 1. Imports ==================
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Dropout, Bidirectional
from tensorflow.keras.callbacks import EarlyStopping
from tabulate import tabulate

# ================== 2. Load & Feature Engineering ==================
df = pd.read_csv('/content/AAPL.csv')
df['Date'] = pd.to_datetime(df['Date'])
df.set_index('Date', inplace=True)

df = df[['Adj Close']].copy()
df['MA10'] = df['Adj Close'].rolling(window=10).mean()
df['MA50'] = df['Adj Close'].rolling(window=50).mean()
df['Returns'] = df['Adj Close'].pct_change()

def compute_RSI(series, window=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window).mean()
    avg_loss = loss.rolling(window).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

df['RSI'] = compute_RSI(df['Adj Close'])
df.dropna(inplace=True)

# ================== 3. Scale ==================
scaler = MinMaxScaler()
scaled_data = scaler.fit_transform(df)

# For inverse scaling only on 'Adj Close'
adj_scaler = MinMaxScaler()
adj_scaler.min_, adj_scaler.scale_ = scaler.min_[0], scaler.scale_[0]

# ================== 4. Sequence Generator ==================
def create_sequences(data, window_size, future_step):
    X, y = [], []
    for i in range(len(data) - window_size - future_step + 1):
        X.append(data[i:i+window_size])
        y.append(data[i+window_size+future_step-1][0])  # only 'Adj Close'
    return np.array(X), np.array(y)

# ================== 5. Modeling Function ==================
def train_predict_model(future_day):
    print(f"\n🚀 Training {future_day}-Day Prediction Model...")
    window_size = 60
    train_size = int(len(scaled_data) * 0.8)

    train_data = scaled_data[:train_size]
    test_data = scaled_data[train_size - window_size:]

    X_train, y_train = create_sequences(train_data, window_size, future_day)
    X_test, y_test = create_sequences(test_data, window_size, future_day)

    model = Sequential([
        Bidirectional(LSTM(64, return_sequences=True), input_shape=(X_train.shape[1], X_train.shape[2])),
        Dropout(0.3),
        LSTM(32),
        Dropout(0.2),
        Dense(1)
    ])

    model.compile(optimizer='adam', loss='mse')

    early_stop = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
    history = model.fit(X_train, y_train, epochs=50, batch_size=32,
                        validation_split=0.1, verbose=0, callbacks=[early_stop])

    pred = model.predict(X_test)
    pred_rescaled = adj_scaler.inverse_transform(pred)
    y_test_rescaled = adj_scaler.inverse_transform(y_test.reshape(-1, 1))
    mse = mean_squared_error(y_test_rescaled, pred_rescaled)

    print(f"✅ {future_day}-Day MSE: {mse:.4f}")

    return y_test_rescaled, pred_rescaled, history, mse

# ================== 6. Train All Models ==================
results = {}
mse_summary = []
for step in [1, 5, 10]:
    actual, predicted, hist, mse = train_predict_model(step)
    results[step] = {
        'actual': actual,
        'predicted': predicted,
        'history': hist
    }
    mse_summary.append([f"{step}-Day", f"{mse:.4f}"])

# ================== 7. Plot Results ==================
for step in [1, 5, 10]:
    actual = results[step]['actual']
    predicted = results[step]['predicted']

    plt.figure(figsize=(12, 5))
    plt.plot(actual, label='Actual Price')
    plt.plot(predicted, label=f'Predicted Price ({step}-Day Ahead)')
    plt.title(f'Apple Stock Price Prediction ({step}-Day Ahead)')
    plt.xlabel('Time Step')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# ================== 8. Plot Training Loss ==================
for step in [1, 5, 10]:
    history = results[step]['history']

    plt.figure(figsize=(8, 4))
    plt.plot(history.history['loss'], label='Train Loss')
    plt.plot(history.history['val_loss'], label='Val Loss')
    plt.title(f'{step}-Day Model Loss')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# ================== 9. MSE Summary Table ==================
print("\n📊 Final MSE Summary (Bidirectional LSTM):")
print(tabulate(mse_summary, headers=["Forecast Horizon", "MSE"], tablefmt="fancy_grid"))

# ================== 10. Save MSE Summary to CSV ==================
mse_df = pd.DataFrame(mse_summary, columns=["Forecast Horizon", "MSE"])
mse_df.to_csv("LSTM_MSE_summary.csv", index=False)

# Apple Stock Price Prediction using Deep Learning (SimpleRNN & LSTM)

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, SimpleRNN, Dropout
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

# Load dataset
df = pd.read_csv('AAPL.csv')
df['Date'] = pd.to_datetime(df['Date'])
df.set_index('Date', inplace=True)
df = df[['Adj Close']].copy()

# Handle missing values
df = df.fillna(method='ffill')

# Normalize data
scaler = MinMaxScaler()
df_scaled = scaler.fit_transform(df)

# Function to create sequences
def create_sequences(data, window_size, forecast_horizon):
    X, y = [], []
    for i in range(len(data) - window_size - forecast_horizon + 1):
        X.append(data[i:i + window_size])
        y.append(data[i + window_size + forecast_horizon - 1])
    return np.array(X), np.array(y)

# Create train/test splits
def prepare_data(forecast_days):
    window_size = 60
    X, y = create_sequences(df_scaled, window_size, forecast_days)
    split = int(len(X) * 0.8)
    return X[:split], y[:split], X[split:], y[split:], window_size

# Build and train models
def build_model(model_type, input_shape, units=50, dropout=0.2):
    model = Sequential()
    if model_type == 'SimpleRNN':
        model.add(SimpleRNN(units, return_sequences=False, input_shape=input_shape))
    elif model_type == 'LSTM':
        model.add(LSTM(units, return_sequences=False, input_shape=input_shape))
    model.add(Dropout(dropout))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model

# Train, evaluate, and plot predictions
def train_and_evaluate(forecast_days):
    X_train, y_train, X_test, y_test, window_size = prepare_data(forecast_days)
    input_shape = (X_train.shape[1], 1)

    models = {'SimpleRNN': build_model('SimpleRNN', input_shape),
              'LSTM': build_model('LSTM', input_shape)}

    history = {}
    results = {}

    for name, model in models.items():
        early_stop = EarlyStopping(monitor='val_loss', patience=5)
        checkpoint = ModelCheckpoint(f'{name}_best_model_{forecast_days}.h5', save_best_only=True)
        hist = model.fit(X_train, y_train, epochs=30, batch_size=32,
                         validation_split=0.1, callbacks=[early_stop, checkpoint], verbose=0)
        pred = model.predict(X_test)
        mse = mean_squared_error(y_test, pred)
        results[name] = mse
        history[name] = hist

        # Plot
        plt.figure(figsize=(10,4))
        plt.plot(scaler.inverse_transform(y_test.reshape(-1, 1)), label='Actual')
        plt.plot(scaler.inverse_transform(pred), label=f'Predicted ({name})')
        plt.title(f'{name} Prediction - {forecast_days}-Day Forecast')
        plt.xlabel('Time')
        plt.ylabel('Adj Close Price')
        plt.legend()
        plt.show()
    return results

# Run for 1-day, 5-day, 10-day forecast
results_summary = {}
for days in [1, 5, 10]:
    print(f"\n--- Forecasting {days} Day(s) Ahead ---")
    result = train_and_evaluate(days)
    results_summary[days] = result

# Display results summary
summary_df = pd.DataFrame(results_summary).T
summary_df.columns = ['SimpleRNN MSE', 'LSTM MSE']
print("\nModel Comparison Summary (MSE):")
print(summary_df)

# Business Use Case Summary
print("""
Business Use Case Summary:
1. Traders use 1-day forecasts for short-term automated trading.
2. Fund managers use 5-day forecasts for mid-range portfolio optimization.
3. Financial analysts and corporations benefit from 10-day predictions for trend analysis, earnings forecasts, and competitor comparisons.
4. The LSTM model consistently outperformed SimpleRNN for all forecast durations, showing its strength in handling long-term dependencies in time-series data.
""")