import pandas as pd
from datetime import datetime
import base64
from io import BytesIO
from django.shortcuts import render
from django.http import JsonResponse
from .utils import list_option_files, SPOT_CSV
from .greeks import compute_greeks
from .iv import implied_volatility
from .backtest import run_straddle_backtest, run_strangle_backtest, run_butterfly_backtest  # if in separate file
from django.core.cache import cache

def dashboard(request):
    files = list_option_files()
    expiry = files[0]['expiry'] if files else 'Unknown'
    return render(request, 'dashboard2.html', {'expiry': expiry})

CACHE_TIMEOUT = 60 * 5  # 5 minutes

def get_greeks(request):
    print("getting greeks...")

    r = float(request.GET.get('r', 0.15))
    cache_key = "full_greeks_dataset"

    # Try to load from cache
    result = cache.get(cache_key)

    if result is None:
        print("Cache MISS → recalculating Greeks data...")
        files = list_option_files()
        spot_df = pd.read_csv(SPOT_CSV, parse_dates=['datetime'])
        spot_df['datetime'] = pd.to_datetime(spot_df['datetime']).dt.round('min')

        allowed_times = ['09:15', '10:15', '11:15', '12:15', '13:15', '15:15']
        result = {}

        for f in files:
            option_df = pd.read_csv(f['path'], parse_dates=['datetime'])
            option_df['datetime'] = pd.to_datetime(option_df['datetime']).dt.round('min')
            option_df['time_only'] = option_df['datetime'].dt.strftime('%H:%M')
            option_df['date_only'] = option_df['datetime'].dt.date

            option_filtered = option_df[option_df['time_only'].isin(allowed_times)]
            option_filtered = option_filtered.drop_duplicates(subset=['datetime'])

            merged = pd.merge(
                option_filtered,
                spot_df[['datetime', 'close']],
                on='datetime',
                how='inner',
                suffixes=('', '_spot')
            )

            greeks_data = []
            for _, row in merged.iterrows():
                S = row['close_spot']
                K = f['strike']
                T = (datetime.strptime(f['expiry'], "%Y-%m-%d") - row['datetime']).days / 365
                if T <= 0:
                    continue

                premium = row['close']
                iv = implied_volatility(S, K, T, r, premium, f['type'])
                if pd.isna(iv):
                    continue

                g = compute_greeks(S, K, T, r, iv, f['type'])
                g['datetime'] = row['datetime'].strftime('%Y-%m-%d %H:%M')
                greeks_data.append(g)

            result[f"{f['strike']}_{f['type']}"] = greeks_data
            print("greeks for", f['strike'], f['type'], "done")

        # Store in cache
        cache.set(cache_key, result, CACHE_TIMEOUT)
    else:
        print("Cache HIT → using cached Greeks data.")

    return JsonResponse({'data': result})


def get_ivs(request):
    spot = float(request.GET.get('spot', 0))
    r = float(request.GET.get('r', 0.15))
    files = list_option_files()
    data = {'call': [], 'put': []}

    for f in files:
        df = pd.read_csv(f['path'])
        close_price = df['close'].iloc[0]
        expiry = datetime.strptime(f['expiry'], "%Y-%m-%d")
        now = df['datetime'].iloc[0]
        T = (expiry - datetime.strptime(now[:10], "%Y-%m-%d")).days / 365
        iv = implied_volatility(spot, f['strike'], T, r, close_price, f['type'])
        if pd.isna(iv): continue
        data[f['type']].append({
            'strike': f['strike'],
            'time': round(T, 4),
            'iv': round(iv, 4)
        })

    return JsonResponse(data)

def get_iv_timeseries(request):
    """Calculate and return implied volatility time series for all options"""
    try:
        print("Getting IV time series...")
        r = float(request.GET.get('r', 0.15))
        
        files = list_option_files()
        if not files:
            return JsonResponse({'error': 'No option files found'}, status=404)
        
        spot_df = pd.read_csv(SPOT_CSV, parse_dates=['datetime'])
        spot_df['datetime'] = pd.to_datetime(spot_df['datetime']).dt.round('min')
        
        # Target times per day for IV calculation
        allowed_times = ['09:15', '10:15', '11:15', '12:15', '13:15', '15:15']
        
        result = {}
        
        for f in files:
            try:
                print(f"Processing IV for: {f['filename']}")
                option_df = pd.read_csv(f['path'], parse_dates=['datetime'])
                option_df['datetime'] = pd.to_datetime(option_df['datetime']).dt.round('min')
                option_df['time_only'] = option_df['datetime'].dt.strftime('%H:%M')
                
                # Filter to specific times
                option_filtered = option_df[option_df['time_only'].isin(allowed_times)]
                option_filtered = option_filtered.drop_duplicates(subset=['datetime'])
                
                # Merge with spot data
                merged = pd.merge(option_filtered, spot_df[['datetime', 'close']], 
                                on='datetime', how='inner', suffixes=('', '_spot'))
                
                iv_data = []
                
                for _, row in merged.iterrows():
                    try:
                        S = row['close_spot']
                        K = f['strike']
                        expiry_date = datetime.strptime(f['expiry'], "%Y-%m-%d")
                        T = (expiry_date - row['datetime']).days / 365
                        
                        if T <= 0:
                            continue
                        
                        premium = row['close']
                        if premium <= 0:
                            continue
                            
                        iv = implied_volatility(S, K, T, r, premium, f['type'])
                        
                        if not pd.isna(iv) and iv > 0:
                            iv_data.append({
                                'datetime': row['datetime'].strftime('%Y-%m-%d %H:%M:%S'),
                                'iv': round(float(iv), 4),
                                'premium': round(float(premium), 2),
                                'spot': round(float(S), 2),
                                'time_to_expiry': round(T, 4)
                            })
                            
                    except Exception as row_error:
                        print(f"Error processing row in {f['filename']}: {row_error}")
                        continue
                
                if iv_data:
                    result[f['filename']] = iv_data
                    print(f"Added {len(iv_data)} IV data points for {f['filename']}")
                    
            except Exception as file_error:
                print(f"Error processing file {f['filename']}: {file_error}")
                continue
        
        print(f"Returning IV data for {len(result)} files")
        return JsonResponse({'data': result})
        
    except Exception as e:
        print(f"Error in get_iv_timeseries: {e}")
        return JsonResponse({'error': str(e)}, status=500)
 
def get_backtest(request):
    strategy = request.GET.get('strategy', '').lower()

    if strategy == 'straddle':
        summary, graph = run_straddle_backtest()
    elif strategy == 'butterfly':
        summary, graph = run_butterfly_backtest()
    else:
        return JsonResponse({'error': 'Invalid strategy selected'}, status=400)
    if graph:
        buffered = BytesIO()
        graph.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
        summary['graph_base64'] = img_str
    else:
        summary['graph_base64'] = None
    return JsonResponse({
        'strategy': strategy,
        'result': summary,
    })
