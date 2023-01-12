#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np


# In[2]:


# let's load the csv data to pandas DataFrame
# Company X's (cx) Data is in three files
cx_sku_weight = pd.read_excel(r"C:\Users\HP\Downloads\Cointab Data Analyst - Challenge (2)\Company X - SKU Master.xlsx")
cx_order = pd.read_excel(r"C:\Users\HP\Downloads\Cointab Data Analyst - Challenge (2)\Company X - Order Report.xlsx")
cx_pincode_zone = pd.read_excel(r"C:\Users\HP\Downloads\Cointab Data Analyst - Challenge (2)\Company X - Pincode Zones.xlsx")

# Courier Companies (cc) data is in two files
cc_rates = pd.read_excel(r"C:\Users\HP\Downloads\Cointab Data Analyst - Challenge (2)\Courier Company - Rates.xlsx")
cc_invoice = pd.read_excel(r"C:\Users\HP\Downloads\Cointab Data Analyst - Challenge (2)\Courier Company - Invoice.xlsx")


# In[6]:


# it will show you all the columns
pd.set_option("display.max_columns",None)
pd.set_option("display.max_rows",None)


# In[7]:


cx_sku_weight


# In[8]:


cx_order


# In[9]:


cx_pincode_zone


# In[10]:


cc_rates


# In[11]:


cc_invoice


# In[12]:


order_report = cx_order.copy() # creat copy of Company X order report for further processing


# In[13]:


order_report.nunique()


# In[14]:


order_report.shape


# In[15]:


order_report.head(20)


# In[16]:


len(order_report['SKU'].isin(cx_sku_weight['SKU'])) # No of order report rows in company x's order


# In[17]:


len(cx_sku_weight['SKU'].isin(order_report['SKU'])) # no of sku numbers in company x' sku master


# In[18]:


pd.merge(order_report, cx_sku_weight, on="SKU") # We check the merged dataframe on common values columns "SKU"
# As we can check one row increased  in the dataframe, which means there's a duplicate value of SKU. we'll try to find and remove it.


# In[19]:


order_report['ExternOrderNo'].nunique() # seems correct


# In[20]:


len(cx_sku_weight['SKU']) # this is correct


# In[21]:


cx_sku_weight['SKU'][cx_sku_weight['SKU'].duplicated()] # checking for duplicates


# In[22]:


cx_sku_weight [cx_sku_weight['SKU'] == 'GIFTBOX202002'] # duplicate found


# In[23]:


# as we can check there are two entries of the same SKU,hence we drop one
#cx_sku_weight.drop(index= 56,inplace= True)
cx_sku_weight = cx_sku_weight.drop_duplicates(subset='SKU', keep="first")


# In[24]:


cx_sku_weight [cx_sku_weight['SKU'] == 'GIFTBOX202002']


# In[25]:


order_report = pd.merge(order_report, cx_sku_weight, on="SKU") # creating a new DF after merging on SKU column
order_report.rename(columns={"Weight (g)": "Weight_(g)_per_unit"},inplace= True) # renaming
order_report.rename(columns={"ExternOrderNo": "Order ID"},inplace= True) 
order_report


# In[26]:


order_report['Weight_per_SKU_per_order'] = order_report['Weight_(g)_per_unit'] * order_report["Order Qty"]


# In[27]:


order_report


# In[28]:


cum_weight_per_order = pd.DataFrame(order_report.groupby(by = ["Order ID"])["Weight_per_SKU_per_order"].sum())
cum_weight_per_order.rename(columns={"Weight_per_SKU_per_order": "Total weight as per X (G)"},inplace= True)
cum_weight_per_order.rename(columns={"ExternOrderNo": "Order ID"},inplace =True)
cum_weight_per_order # cumulative sum of weights in one order


# In[29]:


order_report


# In[30]:


order_report = pd.merge(order_report, cum_weight_per_order, on="Order ID") # merge total weight per order in Kg to order report


# In[31]:


order_report


# In[32]:


order_report['Order ID'].unique() # unique order numbers
# How to create a for loop to select and chang the weights according to our condition values


# In[ ]:


Weight calculation


# In[33]:


def weight_slab (n):
    """ This function converts grams to weights in kg and rounds UP to nearest 0.5 multiple.
    """
    n = n/1000
    return (n + (0.5 - n) % 0.5)


# In[36]:


cum_weight_per_order


# In[37]:


cum_weight_per_order["Weight slab as per X (KG)"] = weight_slab(cum_weight_per_order["Total weight as per X (G)"])
cum_weight_per_order


# In[38]:


order_report["Weight slab as per X (KG)"] = weight_slab(order_report["Total weight as per X (G)"])


# In[39]:


order_report


# In[40]:


#del Result_df


# In[41]:


# Expected output df
Result_df = pd.concat([cc_invoice["Order ID"],cc_invoice['AWB Code']],axis=1)


# In[42]:


Result_df


# In[43]:


# Result_df = pd.merge(Result_df,cum_weight_per_order['Total weight as per X (G)']/1000, on = 'Order ID') # merging on Order ID the total weight in KG CX
# Result_df.rename(columns= {"Total weight as per X (G)": "Total weight as per X (KG)"},inplace = True)
# Result_df

Result_df = pd.merge(Result_df,cum_weight_per_order, on = 'Order ID')
Result_df["Total weight as per X (G)"] = Result_df["Total weight as per X (G)"]/1000
Result_df.rename(columns= {"Total weight as per X (G)": "Total weight as per X (KG)"},inplace = True)

Result_df


# In[44]:


cc_invoice_OrderID_indx = cc_invoice.copy() # created new copy df of courier company invoice copy, 
cc_invoice_OrderID_indx.set_index("Order ID",inplace= True) # set index as Order ID
cc_invoice_OrderID_indx


# In[45]:


Result_df = pd.merge(Result_df,cc_invoice_OrderID_indx["Charged Weight"], on= "Order ID")
Result_df.rename(columns={"Charged Weight": "Total weight as per Courier Company (KG)"},inplace=True)
Result_df


# In[46]:


Result_df["Weight slab charged by Courier Company (KG)"] = weight_slab(Result_df["Total weight as per Courier Company (KG)"]*1000) #using our function weights slab which takes values in grms
Result_df


# In[47]:


cx_pincode_zone


# In[ ]:


#cx_pincode does not have order ID assigned, so we assume we have to keep same sequence as per cc_invoice

#Cross checked the values and found to be of same sequence


# In[48]:


cc_invoice


# In[49]:


cx_pincode_zone.set_index(cc_invoice_OrderID_indx.index,inplace= True) # We assign index to cx_pincode_zone 
cx_pincode_zone


# In[50]:


Result_df = pd.merge(Result_df,cx_pincode_zone["Zone"], on = 'Order ID') #Delivery Zone as per X
Result_df.rename(columns={'Zone':'Delivery Zone as per X'},inplace = True)
Result_df


# In[51]:


Result_df = pd.merge(Result_df,cc_invoice_OrderID_indx["Zone"], on = 'Order ID') # Delivery Zone charged by Courier Company 
Result_df.rename(columns={'Zone':'Delivery Zone charged by Courier Company'},inplace = True)
Result_df


# In[ ]:


Billing calculation
## self defined billing calculator


# In[53]:


cc_rates


# In[54]:


cc_invoice_OrderID_indx


# In[ ]:


# weight = 1.30
# add_multiples_of_half_kg = 0
# fixed_wght = 0.5
# add_wght = weight - 0.5
# while add_wght > 0:
#     add_wght = add_wght- 0.5
#     add_multiples_of_half_kg += 1

# fixed_chrs = 45.4
# add_chrs = 44.8*add_multiples_of_half_kg
# total = fixed_chrs + add_chrs
# tota


# In[55]:


cc_invoice_OrderID_indx


# In[56]:


def rate(target):
    return cc_rates[target][0]


def billing_calc(order_id, weight, zone, Type_of_Shipment):
    if Type_of_Shipment == 'Forward charges':
        shipment_type_fwd = 'fwd'
        fixed_target = "_".join([shipment_type_fwd,zone,'fixed'])
        additional_target = "_".join([shipment_type_fwd,zone,'additional'])
        
        fwd_fxd_rate = rate(fixed_target)
        fwd_add_rate = rate(additional_target)

        fwd_fxd_chrges = fwd_fxd_rate #1

        fwd_add_chrges = add_wght = weight - 0.5 # additional weight
        add_multiples_of_half_kg = 0 # consider additional multiple to be zero
        while add_wght > 0:
            add_wght = add_wght- 0.5
            add_multiples_of_half_kg += 1 # no of multiples of 0.5 KG
        fwd_add_chrges = fwd_add_rate*add_multiples_of_half_kg #2
        # if add_wght == 0:
        #     fwd_add_chrges = 0

        rto_fxd_chrges = 0 #3
        rto_add_chrges = 0 #4 
        #print('ran this fwd')

    else:
        #Type_of_Shipment == 'Forward and RTO charges'
        shipment_type_fwd = 'fwd'
        shipment_type_rto = 'rto'
        fwd_fixed_target = "_".join([shipment_type_fwd,zone,'fixed'])
        fwd_additional_target = "_".join([shipment_type_fwd,zone,'additional'])
        
        rto_fixed_target = "_".join([shipment_type_rto,zone,'fixed'])
        rto_additional_target = "_".join([shipment_type_rto,zone,'additional'])

        fwd_fxd_rate = rate(fwd_fixed_target)
        fwd_add_rate = rate(fwd_additional_target)
        rto_fxd_rate = rate(rto_fixed_target)
        rto_add_rate = rate(rto_additional_target)

        fwd_fxd_chrges = fwd_fxd_rate #1
    
        add_wght = weight - 0.5 # additional weight
        add_multiples_of_half_kg = 0 # consider additional multiple to be zero
        while add_wght > 0:
            add_wght = add_wght- 0.5
            add_multiples_of_half_kg += 1 # no of multiples of 0.5 KG
        fwd_add_chrges = fwd_add_rate*add_multiples_of_half_kg #2
        #if add_wght == 0:
        #    fwd_add_chrges = 0

        rto_fxd_chrges = rto_fxd_rate #3
        
        add_wght1 = weight - 0.5 # additional weight
        add_multiples_of_half_kg_1 = 0 # consider additional multiple to be zero
        while add_wght1 > 0:
            add_wght1 = add_wght1- 0.5
            add_multiples_of_half_kg_1 += 1 # no of multiples of 0.5 KG
        rto_add_chrges = rto_add_rate*add_multiples_of_half_kg_1 #4
        #print('ran this fwd')


    total= round(fwd_fxd_chrges + fwd_add_chrges + rto_fxd_chrges + rto_add_chrges,3)#1+2+3+4

    return  total


# In[57]:


# test the function here
billing_calc(2001806232, 0.73 ,'d','Forward charges')


# In[58]:


df = Result_df.copy()
df


# In[59]:


cc_invoice_OrderID_indx


# In[60]:


cc_invoice_OrderID_indx['Type of Shipment']


# In[61]:


Result_df


# In[62]:


Result_df['Expected Charge as per X (Rs.)']= Result_df['Order ID'] 
#df['Charges Billed by Courier Company (Rs.)'] =df['Order ID']

for i in Result_df.index:
    Result_df['Expected Charge as per X (Rs.)'][i] = billing_calc(Result_df['Order ID'][i],Result_df['Weight slab as per X (KG)'][i],Result_df['Delivery Zone as per X'][i],cc_invoice['Type of Shipment'][i])
    #df['Charges Billed by Courier Company (Rs.)'][i] = billing_calc(df['Order ID'][i],df['Weight slab charged by Courier Company (KG)'][i],df['Delivery Zone charged by Courier Company'][i],cc_invoice_OrderID_indx['Type of Shipment'][i])


# In[63]:


Result_df


# In[64]:


Result_df = pd.merge(Result_df, cc_invoice_OrderID_indx['Billing Amount (Rs.)'], on =['Order ID'])
Result_df.rename(columns={'Billing Amount (Rs.)':'Charges Billed by Courier Company (Rs.)'},inplace= True)
Result_df


# In[69]:


Result_df['Difference Between Expected Charges and Billed Charges (Rs.)'] =  Result_df['Expected Charge as per X (Rs.)'] - Result_df['Charges Billed by Courier Company (Rs.)']


# In[70]:


cc_invoice_OrderID_indx[cc_invoice_OrderID_indx.index == 2001806210]


# In[71]:


Result_df[Result_df['Order ID']== 2001806232]


# In[73]:


#Correctly Charged
Count1 = Result_df[Result_df['Difference Between Expected Charges and Billed Charges (Rs.)']==0].shape[0]

#OverCharged
Count2 = Result_df[Result_df['Difference Between Expected Charges and Billed Charges (Rs.)']<0].shape[0]

# UnderCharged
Count3 = Result_df[Result_df['Difference Between Expected Charges and Billed Charges (Rs.)']>0].shape[0]


# In[74]:


# Correctly Charged
Amount1 = Result_df['Charges Billed by Courier Company (Rs.)'][Result_df['Difference Between Expected Charges and Billed Charges (Rs.)']==0].sum()

# Overcharged
Amount2 = Result_df['Charges Billed by Courier Company (Rs.)'][Result_df['Difference Between Expected Charges and Billed Charges (Rs.)']<0].sum()

# UnderCharged 
Amount3 = Result_df['Charges Billed by Courier Company (Rs.)'][Result_df['Difference Between Expected Charges and Billed Charges (Rs.)']>0].sum()


# In[75]:


summary_df = pd.DataFrame ({'Count': [Count1,Count2,Count3],'Amount':[Amount1,Amount2, Amount3]},index= ['Total Orders - Correctly Charged','Total Orders - Over Charged','Total Orders - Under Charged'])
summary_df


# In[ ]:


Exporting the output files to csv


# In[77]:


# code copied from https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_excel.html
with pd.ExcelWriter('MyResult.xlsx') as writer:  
    summary_df.to_excel(writer, sheet_name='Summary')
    Result_df.to_excel(writer, sheet_name='Calculations', index = False)


# In[ ]:





# In[ ]:




