import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.utils import get_column_letter as L

F='Arial'
hdr_font=Font(name=F,bold=True,color='FFFFFF',size=10); hdr_fill=PatternFill('solid',fgColor='1F4E79')
base=Font(name=F,size=10); bold=Font(name=F,size=10,bold=True); blue=Font(name=F,size=10,color='0000FF')
title=Font(name=F,size=14,bold=True,color='1F4E79'); note=Font(name=F,size=9,italic=True,color='595959')
thin=Side(style='thin',color='D9D9D9')

def sheet_from_df(ws,df,r0=1,widths=None,fmts=None):
    for j,c in enumerate(df.columns,1):
        x=ws.cell(r0,j,c); x.font=hdr_font; x.fill=hdr_fill; x.alignment=Alignment(horizontal='center',vertical='center',wrap_text=True)
    for i,row in enumerate(df.itertuples(index=False),r0+1):
        for j,v in enumerate(row,1):
            x=ws.cell(i,j,v); x.font=base
            if fmts and df.columns[j-1] in fmts: x.number_format=fmts[df.columns[j-1]]
    for j,c in enumerate(df.columns,1):
        ws.column_dimensions[L(j)].width=(widths or {}).get(c,max(14,len(c)+3))
    ws.row_dimensions[r0].height=30

monthly=pd.read_csv('out/monthly.csv'); cat=pd.read_csv('out/category.csv'); state=pd.read_csv('out/state.csv')
delay=pd.read_csv('out/delay.csv'); sellers=pd.read_csv('out/sellers.csv')
wb=Workbook()

# ---------- Monthly ----------
ws=wb.active; ws.title='Monthly'
m=monthly.rename(columns={'purchase_month':'Month','orders':'Orders','revenue':'Revenue (R$)','avg_order_value':'Avg Order Value (R$)','avg_review':'Avg Review (1-5)','pct_late':'% Late'})
m=m[['Month','Orders','Revenue (R$)','Avg Order Value (R$)','Avg Review (1-5)','% Late']]
m.insert(3,'MoM Revenue Growth',None)
sheet_from_df(ws,m,fmts={'Orders':'#,##0','Revenue (R$)':'#,##0','Avg Order Value (R$)':'#,##0.00','Avg Review (1-5)':'0.00','% Late':'0.0'})
n=len(m)
for r in range(3,n+2):
    c=ws.cell(r,4,f'=C{r}/C{r-1}-1'); c.number_format='0.0%;[Red]-0.0%'; c.font=base
ws.cell(2,4,'n/a').font=base; ws.cell(2,4).alignment=Alignment(horizontal='right')
tr=n+3
ws.cell(tr,1,'Total').font=bold
ws.cell(tr,2,f'=SUM(B2:B{n+1})').number_format='#,##0'; ws.cell(tr,3,f'=SUM(C2:C{n+1})').number_format='#,##0'
for c in (2,3): ws.cell(tr,c).font=bold
ws.cell(tr+1,1,'Covers Jan 2017 to Aug 2018 only. Earlier and later months in the data are incomplete. Revenue = item price, excluding freight. Delivered orders only.').font=note
ws.freeze_panes='B2'
ch=BarChart(); ch.title='Monthly Revenue (R$)'; ch.height=8; ch.width=20
ch.add_data(Reference(ws,min_col=3,min_row=1,max_row=n+1),titles_from_data=True); ch.set_categories(Reference(ws,min_col=1,min_row=2,max_row=n+1)); ch.legend=None
ws.add_chart(ch,'I2')

# ---------- Delivery vs Reviews ----------
wd=wb.create_sheet('Delivery vs Reviews')
d=delay.rename(columns={'delivery_bucket':'Delivery vs Estimated Date','orders':'Orders','avg_review':'Avg Review (1-5)','pct_low_reviews':'% Low Reviews (1-2 stars)'})
d['Delivery vs Estimated Date']=d['Delivery vs Estimated Date'].str.replace(r'^\d\. ','',regex=True)
sheet_from_df(wd,d,widths={'Delivery vs Estimated Date':32},fmts={'Orders':'#,##0','Avg Review (1-5)':'0.00','% Low Reviews (1-2 stars)':'0.0'})
wd['E1']='% of Orders'; wd['E1'].font=hdr_font; wd['E1'].fill=hdr_fill; wd['E1'].alignment=Alignment(horizontal='center',vertical='center',wrap_text=True); wd.column_dimensions['E'].width=14
for r in range(2,7):
    wd.cell(r,5,f'=B{r}/SUM($B$2:$B$6)').number_format='0.0%'; wd.cell(r,5).font=base
wd['A8']='On-time or early (rows 2-3)'; wd['A9']='Late (rows 4-6)'; wd['A10']='Review score gap (on-time minus late)'
wd['B8']='=SUM(B2:B3)'; wd['B9']='=SUM(B4:B6)'
wd['C8']='=SUMPRODUCT(B2:B3,C2:C3)/B8'; wd['C9']='=SUMPRODUCT(B4:B6,C4:C6)/B9'; wd['C10']='=C8-C9'
wd['D8']='=SUMPRODUCT(B2:B3,D2:D3)/B8'; wd['D9']='=SUMPRODUCT(B4:B6,D4:D6)/B9'; wd['D10']='=D9-D8'
wd['E8']='=B8/SUM(B2:B6)'; wd['E9']='=B9/SUM(B2:B6)'
wd['E10']=None; wd['D10'].number_format='0.0'; 
for r in (8,9): wd[f'B{r}'].number_format='#,##0'; wd[f'C{r}'].number_format='0.00'; wd[f'D{r}'].number_format='0.0'; wd[f'E{r}'].number_format='0.0%'
wd['C10'].number_format='0.00'
for r in (8,9,10):
    for c in 'ABCDE': wd[f'{c}{r}'].font=bold if c=='A' else base
wd['A12']='Only orders with a review score are included (95,824 orders). D10 shows how many more percentage points of low reviews late orders get.'; wd['A12'].font=note
ch=BarChart(); ch.title='Average review score by delivery timing'; ch.height=8; ch.width=16
ch.add_data(Reference(wd,min_col=3,min_row=1,max_row=6),titles_from_data=True); ch.set_categories(Reference(wd,min_col=1,min_row=2,max_row=6)); ch.legend=None; ch.y_axis.scaling.min=0; ch.y_axis.scaling.max=5
wd.add_chart(ch,'G2')

# ---------- Categories ----------
wc=wb.create_sheet('Categories')
cc=cat.rename(columns={'category':'Category','orders':'Orders','revenue':'Revenue (R$)','avg_review':'Avg Review (1-5)'})
cc.insert(3,'% of Total Revenue',None)
sheet_from_df(wc,cc,widths={'Category':26},fmts={'Orders':'#,##0','Revenue (R$)':'#,##0','Avg Review (1-5)':'0.00'})
k=len(cc)
for r in range(2,k+2):
    wc.cell(r,4,f"=C{r}/Summary!$B$5").number_format='0.0%'; wc.cell(r,4).font=base
wc.cell(k+2,1,'Top 12 combined').font=bold; wc.cell(k+2,3,f'=SUM(C2:C{k+1})').number_format='#,##0'; wc.cell(k+2,4,f'=SUM(D2:D{k+1})').number_format='0.0%'
for c in (3,4): wc.cell(k+2,c).font=bold
wc.cell(k+4,1,'An order with items from two categories counts in both, so order counts can overlap. Revenue does not double count.').font=note

# ---------- States ----------
wsx=wb.create_sheet('States')
s=state.rename(columns={'customer_state':'State','orders':'Orders','revenue':'Revenue (R$)','avg_delivery_days':'Avg Delivery (days)','avg_review':'Avg Review (1-5)'})
s.insert(3,'% of Total Revenue',None); s.insert(4,'Cumulative %',None)
sheet_from_df(wsx,s,fmts={'Orders':'#,##0','Revenue (R$)':'#,##0','Avg Delivery (days)':'0.0','Avg Review (1-5)':'0.00'})
ns=len(s)
for r in range(2,ns+2):
    wsx.cell(r,4,f'=C{r}/SUM($C$2:$C${ns+1})').number_format='0.0%'
    wsx.cell(r,5,f'=SUM($D$2:D{r})').number_format='0.0%'
    for c in (4,5): wsx.cell(r,c).font=base
wsx.freeze_panes='B2'

# ---------- Sellers ----------
wsl=wb.create_sheet('Sellers')
sl=sellers.rename(columns={'seller_id':'Seller ID','seller_state':'State','orders':'Orders','revenue':'Revenue (R$)','avg_review':'Avg Review (1-5)'})
sl.insert(0,'Rank',range(1,len(sl)+1)); sl['Cumulative % of Revenue']=None
sheet_from_df(wsl,sl,widths={'Seller ID':36,'Rank':8},fmts={'Orders':'#,##0','Revenue (R$)':'#,##0','Avg Review (1-5)':'0.00'})
nl=len(sl)
for r in range(2,nl+2):
    wsl.cell(r,7,f'=SUM($E$2:E{r})/SUM($E$2:$E${nl+1})').number_format='0.0%'; wsl.cell(r,7).font=base
wsl.freeze_panes='A2'
wsl['I1']='Seller concentration'; wsl['I1'].font=bold
wsl['I2']='Number of sellers'; wsl['J2']=f'=COUNT(A2:A{nl+1})'
wsl['I3']='Top 10% of sellers (count)'; wsl['J3']='=ROUND(J2*0.1,0)'
wsl['I4']='Share of revenue from top 10%'; wsl['J4']=f'=SUM(E2:INDEX(E2:E{nl+1},J3))/SUM(E2:E{nl+1})'; wsl['J4'].number_format='0.0%'
wsl['I5']='Top 20% of sellers (count)'; wsl['J5']='=ROUND(J2*0.2,0)'
wsl['I6']='Share of revenue from top 20%'; wsl['J6']=f'=SUM(E2:INDEX(E2:E{nl+1},J5))/SUM(E2:E{nl+1})'; wsl['J6'].number_format='0.0%'
for r in range(2,7):
    wsl[f'I{r}'].font=base; wsl[f'J{r}'].font=base
wsl.column_dimensions['I'].width=32; wsl.column_dimensions['J'].width=14
wsl['J2'].number_format='#,##0'; wsl['J3'].number_format='#,##0'; wsl['J5'].number_format='#,##0'

# ---------- Summary (first sheet) ----------
su=wb.create_sheet('Summary',0)
su['A1']='Olist Marketplace Performance and Delivery Analysis'; su['A1'].font=title
su['A2']='Delivered orders, Jan 2017 to Aug 2018 unless stated. Blue cells are hardcoded results from the SQL step, everything else is a formula.'; su['A2'].font=note
rows=[
 ('Metric','Value','Source'),
 ('Total revenue, delivered orders (R$)',13220249,'SQL: order_fact table'),
 ('Total delivered orders',96470,'SQL: order_fact table'),
 ('Unique customers',93350,'SQL: order_fact table'),
 ('Revenue Jan-Aug 2017 (R$)','=SUM(Monthly!C2:C9)','Monthly sheet'),
 ('Revenue Jan-Aug 2018 (R$)','=SUM(Monthly!C14:C21)','Monthly sheet'),
 ('Year-over-year revenue growth (Jan-Aug)','=B9/B8-1','Calculated'),
 ('Share of reviewed orders delivered late',"='Delivery vs Reviews'!E9",'Delivery vs Reviews sheet'),
 ('Avg review, on-time or early orders',"='Delivery vs Reviews'!C8",'Delivery vs Reviews sheet'),
 ('Avg review, late orders',"='Delivery vs Reviews'!C9",'Delivery vs Reviews sheet'),
 ('Review score drop when late','=B12-B13','Calculated'),
 ('Top 3 states share of revenue','=States!E4','States sheet'),
 ('Top 10% of sellers share of revenue','=Sellers!J4','Sellers sheet'),
 ('Repeat customer rate',0.03,'SQL: 2,801 of 93,350 customers ordered more than once'),
]
for i,r in enumerate(rows,4):
    for j,v in enumerate(r,1):
        c=su.cell(i,j,v); c.font=hdr_font if i==4 else base
        if i==4: c.fill=hdr_fill; c.alignment=Alignment(horizontal='center')
for r in (5,6,7,17): su[f'B{r}'].font=blue
for r in (5,6,7,8,9): su[f'B{r}'].number_format='#,##0'
for r in (10,11,15,16,17): su[f'B{r}'].number_format='0.0%'
for r in (12,13,14): su[f'B{r}'].number_format='0.00'
su.column_dimensions['A'].width=46; su.column_dimensions['B'].width=16; su.column_dimensions['C'].width=56
su['A19']='Method notes'; su['A19'].font=bold
notes=['Revenue = item price, excluding freight. Only delivered orders with a delivery date are included.',
 'Delay = actual delivery date minus the estimated delivery date. Positive means late.',
 'Orders with several reviews use the average review score for that order.',
 'Data: Olist Brazilian E-Commerce Public Dataset (Kaggle). Currency is Brazilian reais (R$).']
for i,t in enumerate(notes,20):
    su.cell(i,1,t).font=note
wb.save('out/Olist_Analysis_Summary.xlsx')
print('saved')
