#!/usr/bin/env python
# coding: utf-8

# In[14]:


import requests
import datetime
import json

headers = {"X-API-KEY": "6RNKXW4-W1VMWSY-H8Q28VN-Y08M8WS"}


def get_movies_for_last_year():
    params = {
        'selectFields': 'name movieLength genres rating type votes year budget fees distributors premiere',
        'type': 'movie',
        'sortField': 'votes.kp',
        'sortType': '-1',
        'limit': 4000
    }
    response = requests.get(
        'https://api.kinopoisk.dev/v1.3/movie',
        headers=headers,
        params=params
    )

    return response.text


movies = get_movies_for_last_year()
movies = movies.replace('\xa0', ' ')

with open('data.txt', 'w') as file:
    file.write(str(json.loads(movies)))
    file.flush()

formatted = json.loads(movies)
print(len(formatted['docs']))
# print(json.dumps(formatted, sort_keys=True, indent=4, ensure_ascii=True))


# In[83]:


dict = formatted['docs']
dict


# In[77]:


import pandas as pd
df_l = pd.json_normalize(dict)
df_l


# In[89]:


import re
df_l['genres'] = df_l['genres'].apply(lambda x: re.findall(r"'name': '([^']*)'", str(x)))


# In[90]:


df_l


# In[85]:


df_l['premiere.world'] = pd.to_datetime(df_l['premiere.world'])
df_l['premiere.russia'] = pd.to_datetime(df_l['premiere.russia'])


# In[41]:


df_l


# In[91]:


df_l.dtypes


# In[94]:


missing_values = df_l.isna().sum()
missing_values


# #### Довольно много пропусков, так как всего 4000 наблюдений, а в колонках premiere.digital, rating.await, premiere.dvd,premiere.country, premiere.cinema и premiere.bluray пропусков от 3993 до 3998, то удаляем эти колонки

# In[96]:


row_with_missing_value = df_l[df_l['movieLength'].isnull()]
row_with_missing_value


# #### 1. MovieLength - один пропуск, это фильм "Не игра" -> удаляем строчку
# #### 2. Валюту нужно привести к единому значению -> переводим евро в доллары
# #### 3. Fees.world.value и fees.world.currency - пропуски в fees.world.value, из-за этого пропуски в валюте -> заменяем пропуски на среднее
# #### 4. Fees.russia.value/currency, fees.usa.value/currency, budget.value/currency - аналогичный подход
# #### 5. Distributors.distributor, distributors.distributorRelease - заполнить самым частым дистрибьютером будет не репрезентативно, с другой стороны, отсутсвие дистрибьютера может означатье еще и отсутвие открытых данных или фильм слишком древний и тогда не было дистрибьютеров. При этом, в 398 наблюдениях есть дата релиза дистрибьютором, но дистрибьютера. Мы решили заполнить это 'other'
# #### 6. Premiere.world и premiere.russia имеют пропуски, в мире заполним самым популярным временем)))

# In[99]:


df_l = df_l.drop(df_l[df_l['name'] == 'Не игра'].index) #дроп строчки с фильмом


# In[121]:


df_l_dropped = df_l.drop(['premiere.digital', 'premiere.dvd', 'premiere.country', 'premiere.cinema', 'rating.await', 'premiere.bluray'], axis=1)
#дроп 5 столбцов с большим количеством пропусков


# In[122]:


filtered_df = df_l_dropped[df_l_dropped['fees.world.currency'] == '$']
mfees_value_world = filtered_df['fees.world.value'].mean() # Вычисление среднего значения столбца "fees.world.value" для отфильтрованных строк
mfees_value_world


# In[123]:


filtered_df = df_l_dropped[df_l_dropped['fees.russia.currency'] == '$']
mfees_value_russia = filtered_df['fees.russia.value'].mean()
mfees_value_russia


# In[124]:


filtered_df = df_l_dropped[df_l_dropped['fees.usa.currency'] == '$']
mfees_value_usa = filtered_df['fees.usa.value'].mean()
mfees_value_usa


# In[125]:


filtered_df = df_l_dropped[df_l_dropped['budget.currency'] == '$']
mbudget_value = filtered_df['budget.value'].mean()
mbudget_value


# In[165]:


# Замена пропущенных значений
df_l_dropped['fees.world.value'] = df_l_dropped['fees.world.value'].fillna('mfees_value_world')
df_l_dropped['fees.russia.value'] = df_l_dropped['fees.russia.value'].fillna('mfees_value_russia')
df_l_dropped['fees.usa.value'] = df_l_dropped['fees.usa.value'].fillna('mfees_value_usa')
df_l_dropped['budget.value'] = df_l_dropped['budget.value'].fillna('mbudget_value')

df_l_dropped['fees.world.currency'] = df_l_dropped['fees.world.currency'].fillna('$')
df_l_dropped['fees.russia.currency'] = df_l_dropped['fees.russia.currency'].fillna('$')
df_l_dropped['fees.usa.currency'] = df_l_dropped['fees.usa.currency'].fillna('$')
df_l_dropped['budget.currency'] = df_l_dropped['budget.currency'].fillna('$')


# In[155]:


#Проверка
missing_values1 = df_l_dropped.isna().sum()
missing_values1


# Переходим к переводу валюты

# In[156]:


df_l_dropped.loc[df_l_dropped['fees.world.currency'] == '€', 'fees.world.value'] *= 1.09
df_l_dropped.loc[df_l_dropped['fees.russia.value'] == '€', 'fees.russia.value'] *= 1.09
df_l_dropped.loc[df_l_dropped['fees.usa.value'] == '€', 'fees.usa.value'] *= 1.09
df_l_dropped.loc[df_l_dropped['budget.value'] == '€', 'budget.value'] *= 1.09


# Заполняем пропуски дистрибьютеров на "other"

# In[157]:


df_l_dropped['distributors.distributor'] = df_l_dropped['distributors.distributor'].fillna('other')
df_l_dropped['distributors.distributorRelease'] = df_l_dropped['distributors.distributorRelease'].fillna('other')


# Работаем с колонками премьер

# In[158]:


# Нахождение самого частого значения в столбцах
most_common_world = df_l_dropped['premiere.world'].dt.tz_convert(None).value_counts().idxmax()
most_common_russia = df_l_dropped['premiere.russia'].dt.tz_convert(None).value_counts().idxmax()


# In[159]:


df_l_dropped['premiere.world'] = df_l_dropped['premiere.world'].fillna('most_common_world')
df_l_dropped['premiere.russia'] = df_l_dropped['premiere.russia'].fillna('most_common_russia')


# In[160]:


#Проверка2
missing_values1 = df_l_dropped.isna().sum()
missing_values1


# Все супер, летим дальше

# In[161]:


df_final = df_l_dropped


# In[163]:


import matplotlib.pyplot as plt


# In[167]:


plt.boxplot(df_final['rating.kp'])
plt.show()


# In[169]:


plt.boxplot(df_final['movieLength'])
plt.show()


# In[172]:


plt.hist(df_final['votes.kp'], bins=100, edgecolor='black', log=True)


plt.title('Распределение значений голосов')
plt.xlabel('Значения')
plt.ylabel('Частота')

plt.show()


# In[173]:


plt.hist(df_final['votes.imdb'], bins=100, edgecolor='black', log=True)


plt.title('Распределение значений')
plt.xlabel('Значения')
plt.ylabel('Частота')

plt.show()


# In[ ]:




