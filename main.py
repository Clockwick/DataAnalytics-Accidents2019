import pandas as pd
import os 
import matplotlib.pyplot as plt 
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model  import LinearRegression
from sklearn import metrics, datasets
import seaborn as sns

os.makedirs('./out/', exist_ok=True)  

plt.rc('font', family='Arial')

original_df = pd.read_csv('accidents2019.csv')
# pd.set_option('display.max_columns', None)


def extract_day(x):
    weekday = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    return weekday[x]

def replace_other_to_sunny(x):
    if x == "อื่น ๆ":
        return "แจ่มใส"
    return x

def extract_hour(x):
    return x.strftime('%HH:%mm').split(":")[0].replace("H","")

def extract_date(x):
    return x.strftime('%Y-%m-%d')

df = pd.DataFrame()

df['วันที่'] = pd.to_datetime(original_df['วันที่เกิดเหตุ']).apply(extract_date)

df['วัน'] = pd.to_datetime(original_df['วันที่เกิดเหตุ']).dt.weekday.apply(extract_day)

df['จังหวัด'] = original_df['จังหวัด']

df['อำเภอ'] = None

df['ชั่วโมงของวัน'] = pd.to_datetime(original_df['เวลา']).apply(extract_hour)

df['ความถี่ของอุบัติเหตุ (ครั้ง / ชม.)'] = 0


df['สภาพอากาศ'] = original_df['สภาพอากาศ'].apply(replace_other_to_sunny)

df['latitude'] = original_df['LATITUDE']

df['longtitude'] = original_df['LONGITUDE']


df['วันที่ในเดือน'] = pd.to_datetime(df['วันที่']).dt.day

df['เดือน'] = pd.to_datetime(df['วันที่']).dt.month


freq_per_hour = df.groupby('ชั่วโมงของวัน').count()['ความถี่ของอุบัติเหตุ (ครั้ง / ชม.)']

freq_per_day = df.groupby('วันที่ในเดือน').count()['ความถี่ของอุบัติเหตุ (ครั้ง / ชม.)']

freq_df = pd.DataFrame()
freq_df['วันที่'] = pd.date_range(
    '2019-01-01 00:00:00', '2019-12-31 23:59:59', freq='H').strftime("%Y-%m-%d:%H").tolist()

tmp_df = pd.DataFrame()
tmp_df['วันที่'] = df["วันที่"] + ':' + df['ชั่วโมงของวัน']
tmp_df['ความถี่ของอุบัติเหตุ (ครั้ง / ชม.)'] = 0

freq_df['ความถี่ของอุบัติเหตุ (ครั้ง / ชม.)'] = 0

freq_df = pd.concat(
    [freq_df, tmp_df], ignore_index=True)
freq_df = freq_df.groupby('วันที่').count() - 1
freq_df = freq_df.reset_index()
freq_df['ชั่วโมงของวัน'] = freq_df['วันที่'].apply(lambda x : int(x.split(':')[1]))
freq_df['วันที่'] = freq_df['วันที่'].apply(lambda x : x.split(':')[0])
freq_df['วัน'] = pd.to_datetime(freq_df['วันที่']).dt.weekday.apply(extract_day)

freq_df = freq_df[['วัน','วันที่','ชั่วโมงของวัน','ความถี่ของอุบัติเหตุ (ครั้ง / ชม.)']]


#df = df[['วันที่', 'วัน', 'จังหวัด', 'อำเภอ', 'ชั่วโมงของวัน', 'สภาพอากาศ','latitude','longtitude' ]]
#df.dropna(subset=['latitude', 'longtitude'], inplace=True)
#df = df[df['latitude'] != 0]
#df = df[df['longtitude'] != 0]
#print(freq_df.to_string())
freq_df['ความถี่ของอุบัติเหตุ (เปอร์เซ็นท์)'] = freq_df['ความถี่ของอุบัติเหตุ (ครั้ง / ชม.)'] / freq_df['ความถี่ของอุบัติเหตุ (ครั้ง / ชม.)'].abs().max()
# print(freq_df.to_string())

#print(df.to_string())

day_grouped = freq_df.sort_values(by=['วันที่','ชั่วโมงของวัน']).groupby(freq_df['วัน'])
df_mon = day_grouped.get_group("Mon")
df_tue = day_grouped.get_group("Tue")
df_wed = day_grouped.get_group("Wed")
df_thu = day_grouped.get_group("Thu")
df_fri = day_grouped.get_group("Fri")
df_sat = day_grouped.get_group("Sat")
df_sun = day_grouped.get_group("Sun")

print(df_fri.to_string())

model_df = df_fri[['ชั่วโมงของวัน', 'ความถี่ของอุบัติเหตุ (เปอร์เซ็นท์)']]


# Plot
# df_mon.plot(x="วันที่", y='ความถี่ของอุบัติเหตุ (เปอร์เซ็นท์)', style='o')
# plt.title('แนวโน้มการเกิดอุบัติเหตุในวันจันทร์')
# plt.xlabel('วันที่')
# plt.ylabel('ความถี่ของอุบัติเหตุ (เปอร์เซ็นท์)')
# plt.show()


X = model_df.iloc[:, :-1].values
y = model_df['ความถี่ของอุบัติเหตุ (เปอร์เซ็นท์)'].values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

regressor = LinearRegression()
regressor.fit(X_train, y_train)

y_pred = regressor.predict(X_test)

reg_df = pd.DataFrame({'Actual': y_test, 'Predicted': y_pred})

print('Mean Absolute Error:', metrics.mean_absolute_error(y_test, y_pred))
print('Mean Squared Error:', metrics.mean_squared_error(y_test, y_pred))
print('Root Mean Squared Error:', np.sqrt(metrics.mean_squared_error(y_test, y_pred)))

plt.scatter(X_test, y_test, color="black")
plt.plot(X_test, y_pred, color="blue", linewidth=3)

# sns.scatterplot(data=reg_df,x=X_test,y=y_test);
# sns.regplot(x=X_test, y=y_pred, data=reg_df);

plt.title('Linear Regression')
plt.xlabel('Date (from Jan to Dec)')
plt.ylabel('Frequency (Percentage)')
plt.xticks(())
plt.yticks(())

plt.show()
# df.to_csv('./out/data.csv',index=False)  
# freq_df.to_csv('./out/freq.csv',index=False)