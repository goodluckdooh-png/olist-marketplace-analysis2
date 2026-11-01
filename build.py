import sqlite3, os, pandas as pd, numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import stats
con=sqlite3.connect('olist.db')
# run the SQL file statement by statement; capture result sets
sql=open('olist_analysis.sql').read()
stmts=[s.strip() for s in sql.split(';') if s.strip()]
res=[]
for s in stmts:
    body='\n'.join(l for l in s.split('\n') if not l.strip().startswith('--')).strip()
    if body.upper().startswith('SELECT'): res.append(pd.read_sql(body,con))
    else: con.execute(body)
monthly,cat,state,delay,sellers,repeat=res
con.commit()
os.makedirs('out',exist_ok=True)
pd.read_sql('select * from order_fact',con).round(3).to_csv('out/order_fact.csv',index=False)
pd.read_sql('select * from items_fact',con).round(3).to_csv('out/items_fact.csv',index=False)
for n,d in dict(monthly=monthly,category=cat,state=state,delay=delay,sellers=sellers).items(): d.to_csv(f'out/{n}.csv',index=False)

# ---- charts ----
plt.rcParams.update({'font.family':'DejaVu Sans','axes.spines.top':False,'axes.spines.right':False,'font.size':10})
C1,C2,C3='#1f4e79','#c0392b','#7f8c8d'
# 1 revenue + late %
fig,ax=plt.subplots(figsize=(10,4.8))
ax.bar(monthly.purchase_month,monthly.revenue/1000,color=C1)
ax.set_ylabel('Revenue (R$ thousands)'); ax.set_title('Monthly revenue grew 141% year over year, but late deliveries spiked in Nov 2017 and Feb-Mar 2018')
ax.set_xticks(range(len(monthly))); ax.set_xticklabels(monthly.purchase_month,rotation=60,ha='right')
ax2=ax.twinx(); ax2.plot(monthly.purchase_month,monthly.pct_late,color=C2,marker='o'); ax2.set_ylabel('% of orders delivered late',color=C2); ax2.spines['right'].set_visible(True)
fig.tight_layout(); fig.savefig('out/chart1_revenue_vs_late.png',dpi=160); plt.close()
# 2 delay vs review
fig,ax=plt.subplots(figsize=(8,4.5))
labels=['7+ days\nearly','On time\n(0-7 early)','1-3 days\nlate','4-7 days\nlate','8+ days\nlate']
cols=[C1,C1,'#e67e22',C2,C2]
b=ax.bar(labels,delay.avg_review,color=cols)
for r,v in zip(b,delay.avg_review): ax.text(r.get_x()+r.get_width()/2,v+0.05,f'{v:.2f}',ha='center',fontweight='bold')
ax.set_ylim(0,5); ax.set_ylabel('Average review score (1-5)'); ax.set_title('Orders delivered 4+ days late score under 2.5 on average')
fig.tight_layout(); fig.savefig('out/chart2_delay_vs_review.png',dpi=160); plt.close()
# 3 categories
fig,ax=plt.subplots(figsize=(8,4.8))
c=cat.head(10).iloc[::-1]
ax.barh(c.category,c.revenue/1e6,color=C1); ax.set_xlabel('Revenue (R$ millions)'); ax.set_title('Top 10 categories by revenue')
fig.tight_layout(); fig.savefig('out/chart3_top_categories.png',dpi=160); plt.close()
# 4 state delivery
s=state[state.orders>=500].sort_values('avg_delivery_days')
fig,ax=plt.subplots(figsize=(9,4.5))
ax.bar(s.customer_state,s.avg_delivery_days,color=[C2 if v>15 else C1 for v in s.avg_delivery_days])
ax.set_ylabel('Average delivery time (days)'); ax.set_title('Delivery time by customer state (states with 500+ orders)')
fig.tight_layout(); fig.savefig('out/chart4_state_delivery.png',dpi=160); plt.close()

# ---- stats for write-up ----
f=pd.read_sql('select * from order_fact',con); d=f.dropna(subset=['review_score'])
rho,p=stats.spearmanr(d.delay_days,d.review_score)
late=d[d.delay_days>0].review_score; ot=d[d.delay_days<=0].review_score
tot=sellers.revenue.sum(); n=len(sellers)
print('spearman',round(rho,3),'p',p,'late',round(late.mean(),2),'ontime',round(ot.mean(),2),'pct_late',round(100*(f.delay_days>0).mean(),1))
print('top10pct sellers share',round(100*sellers.revenue.head(int(n*.1)).sum()/tot,1),'sellers',n)
print(repeat)
print('orders',len(f),'revenue',round(f.item_revenue.sum()),'customers',f.customer_unique_id.nunique())
print('top3 cat share', round(100*cat.revenue.head(3).sum()/cat.revenue.sum(),1), 'vs all categories', round(100*cat.revenue.head(3).sum()/f.item_revenue.sum(),1))
