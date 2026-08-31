import csv
import random
from datetime import datetime, timedelta



#parameters
start_date = datetime(2025, 1, 1)
days = 365
base_cpu_usage = 50.0  #base %
base_ram_usage = 40.0  #base %
base_cost = 500.0      #base cost in USD



#seasonality factor(higher on weekdays, lower on weekends)
def get_seasonality(date):
    if date.weekday() < 5: # Mon-Fri
        return random.uniform(1.0, 1.2)
    else: # Sat-Sun
        return random.uniform(0.6, 0.8)



data = []
for i in range(days):
    current_date = start_date + timedelta(days=i)
    
    #upward trend implies scaling
    trend = 1.0 + (i / 365.0) * 0.5  # 50% increase over the year to simulate business scaling
    
    #seasonality
    seasonality = get_seasonality(current_date)
    
    #noise for realistic shi
    noise_cpu = random.uniform(-3, 3)
    noise_ram = random.uniform(-2, 2)
    noise_cost = random.uniform(-20, 20)
    
    cpu = base_cpu_usage * trend * seasonality + noise_cpu
    ram = base_ram_usage * trend * seasonality + noise_ram
    cost = base_cost * trend * seasonality + noise_cost
    


    #bounds
    cpu = min(max(cpu, 1.0), 100.0)
    ram = min(max(ram, 1.0), 100.0)
    cost = max(cost, 10.0)
    
    data.append({
        'Date': current_date.strftime('%Y-%m-%d'),
        'CPU_Usage_Pct': round(cpu, 2),
        'RAM_Usage_Pct': round(ram, 2),
        'Daily_Cost_USD': round(cost, 2)
    })



#csv output!
with open('cloud_billing_dataset.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['Date', 'CPU_Usage_Pct', 'RAM_Usage_Pct', 'Daily_Cost_USD'])
    writer.writeheader()
    writer.writerows(data)
    
print("dataset generated :)")
